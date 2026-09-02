### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-spoofing / cross-tenant webhook attribution - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by HMAC-validating only the raw request body, then hands the caller-supplied `shop-domain` header to the app's handler as the trusted tenant identifier. The header is never covered by the HMAC, so an attacker who can produce (or replay) a validly-signed webhook body can attach an arbitrary `shop-domain` header and have the app process/attribute the webhook to a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read from the unauthenticated header independent of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unauthenticated header) to the handler as the tenant identity for the webhook: [4](#0-3) 

The equality the gem is supposed to enforce is:
`shop authenticated by HMAC == shop used to identify the tenant for the webhook payload`

In this implementation, the HMAC only authenticates the *body bytes*; the `shop-domain` header used to identify which merchant/tenant the webhook belongs to is entirely outside the signed material. Consequently, for any raw body + HMAC pair that is valid for secret `api_secret_key` (e.g., a webhook Shopify legitimately sent to the app for shop A, which the app operator/attacker who controls shop A can observe), the `shop-domain` header can be swapped to shop B's domain while keeping the same body and HMAC, and `HmacValidator.validate` still returns `true`. `WebhookMetadata.new(topic:, shop: request.shop, body:, ...)` then hands the handler `shop = "shop-b.myshopify.com"` even though the signed payload never actually attests to that shop.

### Impact Explanation
This breaks tenant isolation for webhook processing: an app that uses `request.shop` (via `WebhookMetadata#shop`) to look up per-shop state (e.g., session/access-token lookup, order/customer records, billing state) can be made to apply shop-A's legitimately-signed webhook body under shop-B's identity. Depending on how the host app uses the shop field (which is the gem's documented/intended contract — `handler.handle(data: WebhookMetadata.new(... shop: request.shop ...))`), this enables cross-tenant data confusion/corruption purely by manipulating an HTTP header that the gem itself never authenticates. This matches the Critical "cross-tenant access" impact category, since the vulnerability lives in this gem's own webhook verification code path, not in host-app misuse.

### Likelihood Explanation
Exploitability requires the attacker to possess at least one validly-signed webhook body/HMAC pair for the `api_secret_key` in use — which any merchant who has installed the app and receives its own real webhooks already has, without needing any credentials belonging to other tenants. Replaying that body with a modified `shop-domain` (or `x-shopify-shop-domain`) header against the app's webhook endpoint is a simple unauthenticated HTTP request from an "unprivileged internet user" perspective relative to the victim tenant.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered signable material, or otherwise cryptographically bind the header-derived `shop` to the verified body before it is passed to `WebhookMetadata`/handlers. At minimum, `Registry.process` should re-derive/cross-check the shop identity from a value that is part of what Shopify's HMAC actually signs, rather than trusting the `shop-domain` header verbatim.

### Proof of Concept
1. App receives a legitimate Shopify webhook for `shop-a.myshopify.com` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
2. Attacker (who operates/controls `shop-a` and thus legitimately received this webhook) resends the exact same body `B` and HMAC `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present): [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates `H` against `B` only (shop header not included) and returns `true`: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the payload was never signed for shop B, letting shop A's attacker inject/attribute traffic into shop B's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
