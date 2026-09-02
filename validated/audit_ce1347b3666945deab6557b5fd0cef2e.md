## Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop` (and `topic`, `api_version`, `webhook_id`) straight from unauthenticated HTTP headers, but the HMAC signature computed and verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. Any attacker who can obtain one valid `(body, hmac)` pair — trivially available since they own a legitimate shop that has the app installed and receives real Shopify webhooks — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The signature check still passes because the shop is never part of the signed data, so the application will process attacker-controlled/replayed data under a victim shop's identity.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from the (attacker-controlled) HTTP header with no cryptographic binding to the payload: [2](#0-1) 

`HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with `request.shop` as the authoritative tenant identifier: [4](#0-3) 

The equality that should hold is:
`shop_bound_by_hmac == shop_used_for_tenant_attribution`

In this code, the left side is undefined (shop is not part of `to_signable_string`), while the right side is `request.shop`, taken from an unauthenticated header. Because all shops installing the same app share the same `api_secret_key`, any shop that legitimately receives a webhook (a valid `(raw_body, hmac)` pair signed by the app's own secret) can replay it against the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a different, victim shop's domain. `HmacValidator.validate` will still return `true`, since it only re-hashes `raw_body`, and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` pointing at the victim shop.

### Impact Explanation
This breaks the tenant-identity binding that webhook consumers rely on: the HMAC is meant to guarantee "this payload really came from Shopify for shop X," but shop X is never authenticated. A malicious (but otherwise unprivileged) merchant who has installed the app can forge/replay webhooks that the app processes as belonging to a different merchant's shop, i.e., cross-tenant data injection/attribution (e.g., forging an `app/uninstalled` or order/customer webhook against a victim shop, corrupting per-shop state, triggering GDPR data actions, or poisoning tenant-scoped records keyed by `shop`). This matches the "cross-tenant access" Critical-impact category, since the security boundary between tenants of the same app is defined entirely by the (spoofable) `shop` value.

### Likelihood Explanation
Exploitation requires only:
1. Installing the app on any shop (attacker-controlled), which is the normal, unprivileged path any Shopify merchant can take.
2. Capturing one legitimate webhook `(raw_body, x-shopify-hmac-sha256)` pair sent to that attacker-controlled shop (guaranteed to happen once installed).
3. Replaying it to the app's public webhook endpoint with a forged `shopify-shop-domain` header.

No access to `api_secret_key`, access tokens, or the victim's infrastructure is required, making this straightforward for any unprivileged actor who can install the app once.

### Recommendation
Include the shop domain (and ideally `topic`/`webhook_id`) inside the HMAC-covered signable content, or otherwise cryptographically bind the shop claim to the verified payload (e.g., verify that the shop domain matches a value derived from a signed/authenticated source, not a bare header echoed back by the caller). At minimum, downstream consumers should be documented/forced to treat `request.shop` as untrusted unless independently corroborated (e.g., cross-checked against the session/shop that the merchant used during the registration/subscription of that specific webhook topic).

### Proof of Concept
1. App is installed on `attacker.myshopify.com`; app's webhook endpoint receives a real Shopify webhook:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC over raw_body with api_secret_key>`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from that legitimate delivery.
3. Attacker sends a new POST request to the app's webhook endpoint with the same `raw_body` and same `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC only over `raw_body` — signature matches, validation passes.
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, so the app processes attacker-supplied/replayed data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
