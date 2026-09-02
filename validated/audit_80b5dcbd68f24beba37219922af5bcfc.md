## Finding: Webhook shop/topic identity not covered by HMAC binding

### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted for tenant dispatch but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its `to_signable_string` from `@raw_body` alone [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only verifies the HMAC against `to_signable_string` [3](#0-2) , so it never checks that the tenant-identifying headers match what was actually signed by Shopify.

### Finding Description
`Registry.process` calls `Utils::HmacValidator.validate(request)` and, if it passes, dispatches the handler using `request.shop` and `request.topic` taken straight from the request headers [4](#0-3) . The equality this code implicitly assumes is: `shop attributed to WebhookMetadata == shop that the HMAC actually authenticates`. In reality, the HMAC digest is a function of `raw_body` only, independent of the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` header values [5](#0-4) . Consequently, any `(raw_body, hmac)` pair that is valid for one shop/topic combination remains a *valid signature* when replayed with different `shop-domain`/`topic`/`webhook-id` header values, because the verification routine never binds those headers into the signed material.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (populated straight from the unauthenticated header, see `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [6](#0-5) ) to select per-tenant data or trigger tenant-scoped side effects, an attacker who can produce or capture any accepted `(body, hmac)` pair (e.g., from their own store's webhook, or a body whose content is attacker-controlled/predictable) can replay it with a forged `shopify-shop-domain` header pointing at a victim shop and/or a forged `shopify-topic`, and the gem's `HmacValidator` will still report the request as valid. This crosses the tenant boundary the gem is expected to enforce, matching the "Critical - cross-tenant access" impact class.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint plus one legitimately-signed `(body, hmac)` pair for any shop (attacker can be their own free/dev-store tenant, or use webhooks with static/empty bodies like `orders/create` test payloads). No access token, `client_secret`, or privileged credential is required, and the attack is purely a header substitution against `ShopifyAPI::Webhooks::Request.new` / `Registry.process`.

### Recommendation
Bind the tenant-identifying fields into the signed material that `HmacValidator` checks — e.g. include `shop`, `topic`, and `webhook_id` (or otherwise cryptographically bind them to the raw body) in `to_signable_string`, or have `Registry.process` independently verify that the shop/topic in the headers match values embedded in (and covered by) the signed payload before dispatching to handlers.

### Proof of Concept
1. Attacker owns/controls Shop A and triggers a webhook with a known/reusable body (e.g., `{}` or another value they can predict), obtaining a valid `shopify-hmac-sha256` for that exact body.
2. Attacker sends a POST to the app's webhook endpoint with that same raw body and HMAC, but sets `shopify-shop-domain: victim-shop.myshopify.com` and `shopify-topic: <target-topic>`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (no header/body binding check) [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body's HMAC [8](#0-7) .
5. The registered handler executes with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though nothing cryptographically ties that shop value to the signed request.

**Note on uncertainty:** This mirrors Shopify's documented webhook HMAC scheme (HMAC-over-body only), which is a platform-level design choice rather than a coding defect introduced by this gem. Whether it counts as an in-scope "analog" depends on whether the review considers adherence to Shopify's own documented protocol as acceptable behavior; I flag it because it is the closest structural match to the requested bug class (field acted upon but not covered by the HMAC / bytes verified vs. bytes parsed), but I could not find any deviation from Shopify's documented webhook verification contract elsewhere in `lib/shopify_api/**` (OAuth's `AuthQuery#to_signable_string` does include `shop`/`host` in the signed string, and `JwtPayload` validates `aud` against `Context.api_key`, so those paths do not exhibit the same gap).

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/request.rb (L36-38)
```ruby
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
