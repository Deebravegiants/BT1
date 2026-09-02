### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the tenant-identifying `shop-domain` header (and `topic`/`webhook-id`) are read straight from unauthenticated HTTP headers and passed downstream unchecked. `Registry.process` validates only the body/HMAC pair and then hands the caller-supplied `shop` value to the app's webhook handler as trusted tenant identity.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) , and `Request#shop`/`#topic`/`#webhook_id` are pulled directly from HTTP headers with no cryptographic binding to that body [2](#0-1) . `Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)` (which only checks `hmac` against `to_signable_string`, i.e., the body) and then constructs `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id` taken verbatim from the same unauthenticated headers [3](#0-2) . `WebhookMetadata` is a plain struct with `shop` as a `String` field carrying no verification [4](#0-3) .

The identity binding broken is: `HMAC-verified bytes (raw_body) != identity attributed to the request (shop header)`. Any (body, HMAC) pair that is valid for one shop is valid, byte-for-byte, for a forged request carrying an arbitrary `shop-domain` header, because the HMAC algorithm and secret used by an app are shared across all shops that install that app — the signature never encodes which shop it was generated for. This exactly mirrors the "field acted on but not covered by the HMAC" analog: the vault issue omitted a field (settlement fee weight) from a check that gated payment; here the webhook processor omits a field (shop identity) from the check that gates trust, while still acting on it downstream.

### Impact Explanation
This crosses a tenant boundary without needing the app's `client_secret`, an access token, or any privileged credential. An attacker only needs to be an ordinary, unprivileged Shopify merchant/developer who installs the target app on their own store (a normal, unprivileged action — no different from any other real merchant). Doing so, they legitimately receive real webhook deliveries from Shopify containing a valid `(raw_body, x-shopify-hmac-sha256)` pair signed by the app's shared secret for events on their own store. Because the HMAC only binds to the body, the attacker can replay that exact same `(body, hmac)` pair directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with any victim shop's domain. `Registry.process` will accept it as valid (HMAC checks out) and dispatch it to the app's `WebhookHandler#handle` with `WebhookMetadata#shop` set to the forged victim domain. Any application logic that uses this `shop` value to look up per-tenant records, apply mutations, or fetch/associate access tokens for that tenant is now processing attacker-controlled data under a false tenant identity — a cross-tenant access/data-injection primitive.

### Likelihood Explanation
Likelihood is high for any app that relies on this gem's `Webhooks::Registry`/`Request` as documented: the attacker path requires no secret knowledge, no privileged account, and no interception — only a self-service merchant/dev-store install (freely obtainable) plus a normal HTTP POST to the app's public webhook URL with attacker-chosen headers. This is fully reachable through the gem's own API, not dependent on the host app ignoring documented behavior — the gem itself never binds `shop`/`topic`/`webhook_id` into the signature check.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind them to the raw body before trusting them (e.g., require the host app to independently confirm the shop domain against its own known tenant list/stored session before acting, and document this prominently). At minimum, `Utils::HmacValidator.validate` should be changed so `to_signable_string` for webhook `Request` incorporates the shop/topic/webhook-id headers, not the body alone.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development/free store `attacker-shop.myshopify.com` (unprivileged, self-service).
2. Shopify delivers a legitimate webhook to the app's callback URL with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (both fully visible to them, e.g., by making their own store trigger the webhook, or intercepting their own traffic — no secret needed).
4. Attacker sends a new POST request directly to the app's public webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds since the body/HMAC pair is unchanged [6](#0-5) .
6. The app's registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's own webhook body>, ...)` [7](#0-6) , causing the host application to process attacker-supplied data under the victim's tenant identity.

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
