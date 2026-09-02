Based on my investigation, I found a valid analog in this gem's webhook processing.

### Title
Webhook HMAC Covers Only the Raw Body, Not the `shop`/`topic`/`webhook_id` Headers, Allowing Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` verifies the HMAC exclusively against the request body [2](#0-1) . Meanwhile `Registry.process` forwards `request.shop`, `request.topic`, and `request.webhook_id` — all read directly from unauthenticated headers — into `WebhookMetadata` passed to the host app's handler, without ever binding those values to the signature [3](#0-2) .

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) via `shopify_header` [4](#0-3) . None of these header-derived fields are included in `to_signable_string`, which only returns the raw JSON body [1](#0-0) .

`Registry.process` validates only that the HMAC of the body matches the app's shared `Context.api_secret_key` [5](#0-4) , and then unconditionally trusts `request.shop` as the tenant identity forwarded to the handler [6](#0-5) . The gem's own docs confirm host apps are expected to trust `data.shop` as the shop identity of the webhook [7](#0-6) .

The broken identity binding, expressed as an equality that should hold but doesn't: `shop asserted by HMAC-signed bytes == shop credited by Registry.process`. Since `Context.api_secret_key` is the app's single `client_secret` shared across every shop that installs the app (not a per-shop secret), any merchant who has legitimately installed the app and can trigger/replay a webhook delivery with a known body can present a `(raw_body, hmac)` pair that is valid for the app's secret, then freely resubmit that exact HTTP request to the app's webhook endpoint with an attacker-chosen `shopify-shop-domain` header value naming a different, victim shop. Because the shop header is never covered by the signature, `Registry.process` and the handler will treat the forged request as authoritative data belonging to the victim shop.

### Impact Explanation
This breaks the tenant boundary the whole HMAC check exists to enforce: an app is meant to trust that a webhook's `shop` field genuinely identifies the tenant that generated the event. Because only the body is authenticated, one tenant (or anyone who has captured one valid delivery) can inject events attributed to a different tenant, which is a cross-tenant access / data-integrity impact affecting any host application that keys business logic (order processing, redact handling, fulfillment jobs, etc.) off `WebhookMetadata#shop` as documented.

### Likelihood Explanation
Exploitation requires only network access to the app's webhook endpoint (which is, by design, a public HTTP endpoint) plus one previously observed `(raw_body, hmac)` pair for the shared app secret — obtainable by any shop that installs the app and receives even a single real webhook delivery. No access to `api_secret_key`, access tokens, or TLS interception is required.

### Recommendation
Bind the tenant identity into the signed material: either verify that `X-Shopify-Shop-Domain` (and ideally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) is consistent with a shop-scoped secret/session lookup rather than trusting the header directly, or require callers to independently authenticate the shop (e.g., cross-check against an active, stored session for that shop) before acting on `WebhookMetadata#shop`. At minimum, document prominently that `data.shop` is unauthenticated header data and must not be used as a sole tenant-authorization boundary.

### Proof of Concept
1. Install the app on Shop A (attacker-controlled) and receive one legitimate webhook delivery for topic `orders/create`, capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header value `H` (valid because `H = HMAC-SHA256(app_secret, B)`).
2. Replay an HTTP POST to the app's registered webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [8](#0-7) ; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [2](#0-1) ; `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , causing the host app to process attacker-supplied data as if it originated from the victim tenant.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
