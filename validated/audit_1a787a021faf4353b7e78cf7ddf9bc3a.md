### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body [1](#0-0) , while the `shop` (and `topic`/`webhook_id`/`api_version`) values used downstream to identify the tenant are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the body HMAC and then hands the header-derived `shop` straight to the app's handler as the tenant identifier [3](#0-2) . This reproduces the report's bug class: a field ("shop") that is acted upon by the handler is not bound by the same cryptographic check ("hmac") that authenticates the payload — the identity binding `hmac_verified(shop) == shop_used_by_handler` does not hold.

### Finding Description
`VerifiableQuery#to_signable_string` is the sole input to HMAC verification [4](#0-3) , and `HmacValidator.validate` simply recomputes `HMAC(secret, to_signable_string)` and compares it with the supplied `hmac` [5](#0-4) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . All other attributes the gem exposes — `shop`, `topic`, `webhook_id`, `api_version` — come from HTTP headers that are never included in the signed string [6](#0-5) .

`Registry.process` raises only if the body HMAC fails, then immediately builds `WebhookMetadata` using `request.shop`, which is passed to the app-provided `handler.handle` as the merchant identity for that event [3](#0-2) , and `WebhookMetadata#shop` is a plain `String` const with no additional verification [7](#0-6) .

Since the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is identical for every shop that has the app installed, any merchant who installs the app can obtain a genuinely-signed webhook for their own store (e.g. a `shop/redact`/`orders/create` webhook with a body they control or a body that is shop-agnostic), then relay that request to the app's webhook endpoint after rewriting the `X-Shopify-Shop-Domain` / `Shopify-Shop-Domain` header to a victim shop's domain. Because the header is not part of the signed content, `HmacValidator.validate` still succeeds, and `Registry.process` dispatches the event to the handler labelled as coming from the victim shop.

### Impact Explanation
This breaks the tenant binding "shop authenticated == shop acted upon", enabling cross-tenant webhook spoofing: an app that keys any state (session lookups, per-shop counters, uninstall/redact handling, order/customer records) by `WebhookMetadata#shop` can be made to attribute attacker-controlled webhook data to another merchant's tenant. This matches the "Critical - cross-tenant access" impact category, since it lets one unprivileged installer of the app inject events under another tenant's identity without ever possessing that tenant's credentials.

### Likelihood Explanation
Any developer/merchant who can install the target app on their own store obtains valid signed webhook traffic for that store at will (by triggering normal store events), and only needs to intercept/replay the HTTP request with a modified header — no access to `api_secret_key`, tokens, or TLS interception is required. The library provides no header-binding, so exploitation is fully within the capability of an "unprivileged internet user" who is simply a legitimate customer/merchant of the platform running this gem.

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the signed content checked by `HmacValidator`, or otherwise cryptographically bind the `shop` header to the payload before trusting it. Concretely, change `Webhooks::Request#to_signable_string` to incorporate the shop/topic headers (this requires coordinating with Shopify's own webhook signing scheme, since Shopify currently signs raw body only) — at minimum, document and encourage consumers to independently verify `WebhookMetadata#shop` against records established via OAuth/session storage before trusting it for any tenant-scoped operation, since the header itself carries no integrity guarantee in this gem.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a store event so Shopify sends a legitimately HMAC-signed webhook to the app's endpoint, e.g. body `{}` with headers:
   - `X-Shopify-Hmac-Sha256: <valid hmac of "{}">`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `X-Shopify-Topic: shop/redact`
3. Attacker intercepts the request before/at the app's ingress and rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, leaving body and HMAC header untouched.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)` is constructed by the host app exactly as with a genuine request [8](#0-7) .
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `"{}"` only and succeeds because the body and HMAC are unmodified [9](#0-8) .
6. `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", ...)` is dispatched to the app's handler, which processes the event as if it originated from `victim-shop.myshopify.com`, despite it never having sent anything [10](#0-9) .

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-15)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
