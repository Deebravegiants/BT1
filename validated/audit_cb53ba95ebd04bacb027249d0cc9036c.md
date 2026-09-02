### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates only the raw JSON body via HMAC, but exposes `shop` (and `topic`, `api_version`, `webhook_id`) from HTTP headers that are never part of the signed payload. `Registry.process` trusts `request.shop` as the tenant identity when dispatching to the app's handler, even though that value was never bound by the HMAC check.

### Finding Description
The identity binding that should hold is:
`HMAC_valid(secret, signed_bytes) == true` implies `signed_bytes` fully determine the tenant (`shop`) the payload is attributed to.

In this gem, `to_signable_string` returns only the raw body: [1](#0-0) 

but `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is completely outside the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then unconditionally forwards `request.shop` (the unauthenticated header value) to the app's handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` simply recomputes the HMAC over `verifiable_query.to_signable_string` and compares — it has no notion of `shop` at all: [4](#0-3) 

So two requests with identical bodies (same shape of event, e.g. an `orders/create` payload with matching timestamps/IDs) produce the same valid HMAC regardless of which `shop-domain` header is attached. An attacker who obtains one genuine webhook delivery (their own shop's webhook, which they legitimately receive as the shop owner/app install) can replay the exact same body+HMAC to the app's webhook endpoint while substituting a different shop's domain in the header. The gem will report `Utils::HmacValidator.validate(request)` as `true` and hand the handler a `WebhookMetadata` claiming the wrong `shop`: [5](#0-4) 

This is the same bug class as the referenced report: an action (webhook processing / tenant attribution) is performed based on a value (`shop`) that is not covered by the cryptographic check (`HMAC`) meant to authenticate the whole request, letting an attacker control an unverified field while satisfying the verified check on a different field.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as returned by this gem) to key data writes, cache entries, or session/token lookups per-tenant, an attacker can force the app to process attacker-supplied body content under an arbitrary victim shop's identity, since the gem itself asserts the request is "valid" via `HmacValidator.validate`. This is a cross-tenant identity confusion enabled directly by the gem's request/validation design, matching the High-impact category (scope/expiry-style check bypass via an unbound identity field).

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain at least one genuine signed webhook body from their own shop (trivial — any merchant installing the app receives real webhooks) and being able to send arbitrary HTTP requests to the app's public webhook endpoint (also trivial, as endpoints are public). No `api_secret_key` or privileged credential is required — only a normal, unprivileged webhook recipient replaying their own valid payload with a modified header.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signed payload check, or otherwise cryptographically bind the `shop-domain` header to the signature (e.g., verify the header against a separately established relationship, or require the caller to also independently confirm the destination shop before trusting `request.shop`). At minimum, document clearly that `request.shop` is unauthenticated and must not be used as sole tenant-identifying data without additional verification.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; receive a legitimate webhook delivery with body `B` and valid header `X-Shopify-Hmac-Sha256: H` (where `H = HMAC(secret, B)`).
2. Replay an HTTP POST to the app's webhook endpoint with the same body `B`, same `X-Shopify-Hmac-Sha256: H`, but header `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: spoofed_headers)` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H`, per `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`.
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, per `lib/shopify_api/webhooks/registry.rb:198-199`, even though `victim-shop.myshopify.com` never signed or sent this request.

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
