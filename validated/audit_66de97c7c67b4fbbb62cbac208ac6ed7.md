### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw body only, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header. `Registry.process` validates the HMAC against the body and then hands the handler the shop value taken from that unauthenticated header, breaking the binding `HMAC(payload) == HMAC(payload, shop)`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header without any cryptographic binding to the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the shared `api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop`, which came from the unauthenticated header, not from anything verified by the HMAC: [4](#0-3) 

This differs from `Auth::Oauth::AuthQuery`, where `shop` (and `host`, `state`, etc.) are explicitly included in `to_signable_string` and thus bound to the HMAC: [5](#0-4) 

The identity-binding equality that should hold is `HMAC_valid(body) ⇒ shop == shop_that_produced(body)`. Because the header carrying `shop` is excluded from the signed content, an attacker who can capture (or is legitimately sent, e.g. via a test/dev endpoint they control) one valid `(raw_body, hmac)` pair from Shopify for the app can resend that exact body/HMAC pair to the merchant's webhook endpoint with an arbitrary, attacker-chosen `shopify-shop-domain` header. `HmacValidator.validate` will still pass (it never looks at the shop header), and `Registry.process` will dispatch `WebhookMetadata` carrying the attacker-chosen `shop` value to the host application's handler, which typically uses `data.shop` to look up the tenant's session/store record and perform tenant-scoped side effects (e.g., `Shop.find_by(shopify_domain: data.shop)`).

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC is supposed to provide: the gem states "HMAC validated" but the shop identity used for tenant routing downstream is not part of what was validated. A host app that trusts `WebhookMetadata#shop` as authenticated (which is the documented contract of this gem's webhook verification) can be tricked into applying webhook data intended for shop A to shop B's tenant record — a cross-tenant data-confusion vector purely due to a gap in this gem's HMAC coverage, matching the "field acted on but not covered by the HMAC" bug class.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimate `(raw_body, hmac)` pair for the app (e.g., by triggering a webhook on their own store, since the HMAC secret is per-app not per-shop) and then replay it against the same publicly-reachable webhook endpoint with a modified `shop-domain` header — no access token, `client_secret`, or privileged account is required. This is a realistic external-attacker path given webhook endpoints are public HTTP endpoints and any merchant/app-developer can generate a valid, signed sample payload for their own shop.

### Recommendation
Include the shop-identifying header (`shopify-shop-domain`) in the HMAC-signable content for webhooks, e.g. incorporate `shop`, `topic`, and `webhook_id` into `to_signable_string` (or otherwise cryptographically bind them, similar to `AuthQuery`), and validate that the signed shop matches the value later exposed via `WebhookMetadata#shop`.

### Proof of Concept
1. App developer registers a webhook and, in their own dev shop `attacker-shop.myshopify.com`, receives (or synthesizes via the same shared secret) a valid webhook delivery: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker sends the same `B` and `H` to the merchant app's webhook endpoint but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` accepts the request (all required headers present) — [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `to_signable_string` (`@raw_body`), unaffected by the shop header change — [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from/for `attacker-shop.myshopify.com`, causing the host app to apply attacker-controlled webhook data to the victim tenant.

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
