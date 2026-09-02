### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook to a tenant come from unsigned HTTP headers. This mirrors the LT.sol root cause pattern: a value that is acted upon (`staked`/here, the `shop` used for tenant attribution) is not actually covered/protected by the mechanism meant to guarantee its integrity (the `MIN_SHARE_REMAINDER` invariant/here, the HMAC digest).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never part of the signed content: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `HMAC(api_secret_key, verifiable_query.to_signable_string)`: [3](#0-2) 

`Registry.process` then trusts the header-derived `request.shop` to attribute the event to a tenant, without any check binding that shop value to the signature: [4](#0-3) 

Because the HMAC key (`Context.api_secret_key`) is the same app-wide secret shared across every merchant/tenant using the app, and the signature only certifies the body bytes (not which shop the event belongs to), an equality that should hold — "shop claimed in the unsigned header" == "shop that the signature actually authenticates" — does not hold. Any request whose body+HMAC pair is valid (e.g., replayed or produced from a body an attacker can obtain/predict for their own shop) can have its `shopify-shop-domain` header swapped to a victim shop's domain and will still pass `HmacValidator.validate`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an unprivileged holder of one valid (shop, body, hmac) tuple for the app (e.g., their own shop, which they legitimately control as an app merchant) can cause the receiving application to process a webhook as if it came from a different shop, since `WebhookMetadata.shop` handed to the handler is entirely derived from an unauthenticated header. This is a cross-tenant access vector as defined in scope (Critical): an app's business logic keyed on `data.shop` (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`, inventory/order webhooks) can be triggered against a shop the attacker does not own.

### Likelihood Explanation
Exploitation requires only a network-reachable webhook endpoint and one valid (body, hmac) pair — obtainable by the attacker for their own tenant, since they are a legitimate merchant of the app and receive webhooks for their own shop, or by replaying an intercepted webhook. No `api_secret_key`, access token, or privileged access is required to perform the header substitution itself.

### Recommendation
Include the shop domain (and other identity-relevant headers such as topic/webhook-id/api-version) in the string that is HMAC-verified, or otherwise cryptographically bind the `shop` value to the signed payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document and require host applications to independently verify that the `shop` header corresponds to a shop with a stored, previously-authenticated session/installation before acting on webhook data, since the library's own `HmacValidator` does not provide that guarantee.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com`; attacker controls that shop and can trigger/capture a legitimate webhook delivery, e.g. `{}` body for `app/uninstalled`, yielding a valid `x-shopify-hmac-sha256` for that exact raw body under the app's shared `api_secret_key`.
2. Attacker resends the same raw body and the same (still-valid) HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop using the same app).
3. `ShopifyAPI::Webhooks::Request.new` parses headers normally; `HmacValidator.validate` recomputes HMAC over `@raw_body` only and it matches, per `lib/shopify_api/webhooks/request.rb` lines 35-38 and `lib/shopify_api/utils/hmac_validator.rb` lines 26-31.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is `"shop-b.myshopify.com"`, per `lib/shopify_api/webhooks/registry.rb` lines 188-199 — the app now processes an uninstall/redact/etc. event attributed to `shop-b`, a tenant the attacker does not control.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
