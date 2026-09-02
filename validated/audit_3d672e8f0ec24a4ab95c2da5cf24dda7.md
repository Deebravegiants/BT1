### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant shop-domain spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC validated by `HmacValidator.validate` only proves the integrity of the JSON body bytes — it never binds the `shop` value read from the `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates the HMAC and then forwards `request.shop` straight into `WebhookMetadata` handed to the app's handler as the tenant identifier, with no additional check that the header matches the body/signature [3](#0-2) .

### Finding Description
This is the same "field acted on but not covered by the HMAC" bug class as the external report (which found that `requestRedeem()` used shares/assets it never protected via the accounting invariant). Here, `WebhookMetadata.shop` is the field acted on by the app (used for merchant/tenant routing, data isolation, look-ups, etc.), but the binding

```
HMAC(body_bytes) == HMAC(body_bytes)         # what is actually verified
shop_header == shop_that_produced_the_body    # what is implicitly assumed, but never checked
```

is never enforced. `to_signable_string` (used inside `HmacValidator.validate_signature`, `lib/shopify_api/utils/hmac_validator.rb:26-31`) only feeds `@raw_body` into the signature computation. Any attacker holding one legitimate `(raw_body, hmac)` pair — trivially obtainable by owning a store with the same app installed, or from a leaked/replayed request — can resend that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header for another merchant's shop. The HMAC still validates because the header is not part of the signed data, yet the gem hands the attacker-controlled `shop` value to the handler as if it were authenticated. Note by contrast that `Auth::Oauth::AuthQuery#to_signable_string` explicitly includes `shop` in the signed data for OAuth callbacks [4](#0-3) , showing the gem's own convention is to bind `shop` into the HMAC — the webhook path breaks that convention.

### Impact Explanation
This crosses a tenant boundary: an app relying on `WebhookMetadata#shop` (the documented, gem-provided field for identifying which merchant a webhook belongs to) to select per-shop state, credentials, or data can be tricked into attributing a legitimate payload to the wrong shop, or attacker-supplied `shop` values can be injected into per-tenant processing while riding on a validly-HMAC'd body. This matches the "cross-tenant access" impact tier.

### Likelihood Explanation
Likelihood is high for any app that has ever received one legitimate webhook (either from its own store or, if it is a multi-merchant app, one connected merchant): the attacker only needs to capture a single valid `(raw_body, X-Shopify-Hmac-Sha256)` pair and can then replay it with a forged `shop-domain` header at will, since the header is fully attacker-controlled input to `Request.new(headers:)` and is never re-validated against the signature.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the signed data verified by `HmacValidator`, or independently re-verify that `request.shop` matches an expected/allow-listed shop before dispatching to `WebhookHandler#handle`. At minimum, document clearly that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com` with body `B` and valid header `X-Shopify-Hmac-Sha256: H` (where `H = HMAC(secret, B)`).
2. Attacker resends the exact same `raw_body: B` and `hmac-sha256: H`, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not correlation) [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, request.to_signable_string)` = `HMAC(secret, B)` = `H`, so validation succeeds [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(... shop: "shop-b.myshopify.com" ...)` even though the body actually belongs to `shop-a` [7](#0-6) , achieving cross-tenant shop-domain spoofing without possessing `shop-b`'s data.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
