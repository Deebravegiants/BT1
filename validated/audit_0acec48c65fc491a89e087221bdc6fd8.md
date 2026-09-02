### Title
Webhook shop-domain spoofing via HMAC that only covers the request body, not the `shop` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable content solely from the raw request body, while the `shop` identity used by `Registry.process` to route/attribute the webhook is read from an HTTP header that is never included in the signed content. This breaks the binding `bytes verified == bytes that determine tenant identity`, allowing an attacker who can obtain one valid `(body, hmac)` pair for the app to replay it against the app's webhook endpoint while spoofing the `shop-domain` header to a different tenant that has the same app installed, since the HMAC secret (`client_secret`) is shared across all shops that installed the app.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers and are not part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the HMAC, so it never validates the `shop` header: [3](#0-2) 

`Webhooks::Registry.process` passes `request.shop` straight into `WebhookMetadata` after only checking the body HMAC — the tenant-identifying field is trusted without being covered by the signature: [4](#0-3) 

The identity binding that should hold is: `HMAC-verified bytes == bytes that determine which shop/tenant the webhook is attributed to`. Here it does not — the HMAC only proves the body came from a holder of `client_secret` (the app's single shared secret across all installs), but the `shop` value that the host application's handler uses to select/write tenant data is an unauthenticated header value.

### Impact Explanation
The `client_secret`/HMAC key is per-app, not per-shop. Any tenant of the app (or anyone able to observe a legitimately delivered webhook, e.g. by triggering an event in their own store) can capture a valid `(body, hmac)` pair and resubmit it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header changed to a victim shop that also has the app installed. Because the gem's HMAC check does not cover this header, `Registry.process` will still accept the request and dispatch it to the handler with `shop` set to the attacker-chosen victim domain. This crosses the tenant boundary the gem is expected to enforce and can lead to cross-tenant data writes/state corruption in host applications that trust `WebhookMetadata#shop` for tenant scoping — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (a) the attacker has access to install the target app on their own shop or otherwise observe one legitimate webhook body+HMAC for that app, and (b) another shop with the same app installed exists as a target. No access token, `api_secret_key`, or privileged account is needed — this is achievable by an ordinary merchant/customer interacting with a multi-tenant app, which fits the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified content, or independently verify that the `shop-domain` header corresponds to a shop that is expected to be delivering this specific signed body (e.g., by additionally validating shop against session storage keyed off a signed claim, not a raw header). At minimum, document that host applications must not trust `WebhookMetadata#shop` for tenant attribution unless it is cross-checked against an independently verified source.

### Proof of Concept
1. App is installed on Shop A and Shop B (same `client_id`/`client_secret`).
2. Attacker controls Shop A and triggers a webhook (e.g., `orders/create`), capturing the raw POST body and its `X-Shopify-Hmac-Sha256` value sent to the app's webhook endpoint.
3. Attacker resends the identical body and HMAC header to the same endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `Webhooks::Request.new` parses headers and body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the shared secret: [5](#0-4) 
5. The handler is invoked with `shop: "shop-b.myshopify.com"` even though the payload actually originated from Shop A, achieving cross-tenant webhook injection.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
