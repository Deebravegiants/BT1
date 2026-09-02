### Title
Webhook shop-domain (and topic/webhook-id) headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then forwards `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by that HMAC — directly to the application's webhook handler as trusted metadata.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`, dispatching it to the registered handler: [3](#0-2) 

The identity binding that should hold is: `shop-header == shop-that-produced-this-signature`. Because `to_signable_string` only covers the body, this equality is never checked — the HMAC only proves "this body was signed with `api_secret_key`," not "this body/event belongs to the shop named in the `shop-domain` header." Since a single app has one `api_secret_key` shared across every shop that installs it, any unprivileged actor who installs the public app on their own store receives genuine webhooks with valid HMACs for their own shop. That attacker can replay the same body+HMAC pair while rewriting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) headers to point at any victim shop domain, and `Registry.process` will accept it as authentic, passing the forged shop identity to the handler unmodified. This mirrors the report's bug class exactly: a field acted upon (`shop`) that is not covered by the integrity check (HMAC), letting an attacker desynchronize "the shop the signature actually vouches for" from "the shop the code believes it received data for."

### Impact Explanation
This is a cross-tenant identity confusion primitive reachable by any unprivileged party who can install the app once (a normal, unprivileged flow for public apps) and does not require the `api_secret_key`, an access token, or any leaked credential — it uses the attacker's own legitimately-issued webhook. Any host application logic that keys off `WebhookMetadata#shop` (e.g., looking up the shop's stored access token/session, applying shop-scoped business logic, writing multi-tenant records) can be tricked into acting under a spoofed victim shop identity, i.e. cross-tenant access — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only: (1) install the target app on an attacker-controlled development store (freely available for public apps), (2) capture one genuine webhook (body + valid `x-shopify-hmac-sha256`), (3) replay it to the app's webhook endpoint with the `shop-domain` (and optionally `topic`/`webhook-id`) header swapped to the victim's domain. No secret material or privileged access is needed, making this practically exploitable by any external actor able to reach the webhook endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook-id) to the signed payload before trusting them: either require callers to independently verify `request.shop` against an authenticated source of truth (e.g., a known/installed-shop allow-list correlated with the delivery, not merely trusting the header), or extend `VerifiableQuery`/`to_signable_string` for webhook requests so the signature check fails if `shop`, `topic`, or `webhook_id` are altered, consistent with how `Auth::Oauth::AuthQuery#to_signable_string` already includes `shop` in its signed fields.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev store `attacker.myshopify.com`, receiving a legitimate webhook:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - Body: `{"id":1,...}`
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header set successfully (no header-body binding check) [4](#0-3) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body` (unchanged), and then dispatches the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` reporting `shop: "victim.myshopify.com"` [3](#0-2) .
5. Any host-app logic trusting `data.shop` now operates under the spoofed victim identity despite the event actually originating from the attacker's own store data.

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
