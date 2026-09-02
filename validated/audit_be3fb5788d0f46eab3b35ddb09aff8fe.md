### Title
Webhook shop-domain and topic identity are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC over the raw body only, while the `shop`, `topic`, and `webhook_id` values that `Registry.process` treats as authoritative tenant/event identity are read from unauthenticated HTTP headers that are never included in the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` verifies the HMAC solely against this signable string [2](#0-1) . Meanwhile, `Request#shop`, `Request#topic`, and `Request#webhook_id` are pulled directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) with no cryptographic binding to those headers [3](#0-2) .

`Registry.process` validates only the HMAC and then passes `request.shop` and `request.topic` straight into `WebhookMetadata`, which the host application's handler treats as the authenticated tenant/event identity: [4](#0-3) 

The equality the HMAC is supposed to guarantee is:
`HMAC(secret, signed_bytes) == received_hmac` ⟺ `signed_bytes` is authentic for `(shop, topic, webhook_id)`.

In this implementation the actual equality only proves:
`HMAC(secret, raw_body) == received_hmac`, with `(shop, topic, webhook_id)` supplied out-of-band and unauthenticated.

Because a single `api_secret_key` is shared across every shop that installs the app, any shop that installs the app can obtain a validly-signed webhook body (e.g. for `orders/create`) delivered to their own endpoint. That merchant — an ordinary unprivileged installer, not a privileged actor — can then replay the exact same raw body to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic`/`shopify-webhook-id` headers) to claim it belongs to a different shop. `HmacValidator.validate` will still pass, because the HMAC never covered those headers, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop's identity while carrying the attacker's payload.

### Impact Explanation
This breaks the tenant-identity binding that webhook handlers rely on to scope side effects (e.g., updating records, revoking data, or reacting to `shop/redact`) to the correct shop. An attacker who legitimately installs the app on their own store can forge webhook deliveries attributed to an arbitrary victim shop domain, causing the host application to process attacker-controlled data under another tenant's identity — a cross-tenant confusion condition reachable purely by replaying/re-sending HTTP requests, without any access token, `client_secret`, or privileged account.

### Likelihood Explanation
The attacker only needs the ability to install the target app on a shop they control (a standard, unprivileged capability for any Shopify merchant/developer) and the ability to send arbitrary HTTP requests with custom headers to the app's public webhook endpoint. Both are trivial and require no secret material beyond what Shopify legitimately gives any installer.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook_id`, `api-version`) in the HMAC-signed material — e.g., have `to_signable_string` canonicalize and include these header values alongside the raw body — so the HMAC binds the full delivery context, not just the payload bytes. Alternatively, have `Registry.process` independently verify that `request.shop` corresponds to a shop session/registration the app expects before trusting it for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`). Shopify sends a POST to the app's webhook URL with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body over api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
2. Attacker captures the raw body and the valid `x-shopify-hmac-sha256` value.
3. Attacker resends the identical raw body and HMAC header to the same endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `HmacValidator.validate` recomputes `HMAC(secret, raw_body)` [2](#0-1)  — it matches, since the body is unchanged.
5. `Registry.process` raises no error and invokes the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)` [4](#0-3) , causing the host app to act on attacker data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
