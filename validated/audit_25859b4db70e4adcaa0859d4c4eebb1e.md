### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with the app's shared `client_secret` [2](#0-1) . The `shop` (from the `X-Shopify-Shop-Domain` header), `topic`, `api_version`, and `webhook_id` values are read straight from attacker-controllable headers and are never part of the signed material [3](#0-2) . `Registry.process` validates the HMAC and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` that is handed to the host application's handler as the authoritative source of "which shop this event belongs to" [4](#0-3) , and `WebhookMetadata.shop` is a plain, unauthenticated `String` field [5](#0-4) .

### Finding Description
The identity binding this code implicitly claims to provide is:
`hmac_valid(request) == true` ⟹ `request.shop is the shop that produced this event`

In reality the equality that actually holds is only:
`hmac_valid(request) == true` ⟹ `request.raw_body was signed with this app's client_secret`

Because Shopify signs webhooks with the **app-level** `client_secret` (shared across every shop that has the app installed) rather than a per-shop secret, and because the signature covers only `@raw_body` [1](#0-0) , any attacker who has installed the app on their own (unprivileged) shop can:
1. Receive a legitimate webhook to their own endpoint, capturing a `(raw_body, X-Shopify-Hmac-Sha256)` pair that is valid under the shared secret.
2. Replay that exact body/HMAC pair to the host application's webhook endpoint while rewriting the `X-Shopify-Shop-Domain` header to any victim shop's domain (and optionally the topic/webhook-id headers).
3. `Utils::HmacValidator.validate(request)` returns `true` because it only checks the body signature [6](#0-5) .
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the forged headers and invokes the host's `handler.handle` with `shop` set to the victim tenant [7](#0-6) .

This lets the attacker impersonate arbitrary other tenants for webhook processing (e.g., forging `app/uninstalled`, `shop/redact`, `orders/create`, or any topic-specific handler logic keyed off `data.shop`) — a direct cross-tenant identity confusion enabled entirely by this gem's `Request`/`Registry`/`WebhookMetadata` implementation, with no dependency on host misconfiguration.

### Impact Explanation
This breaks the tenant isolation guarantee the library is expected to provide when it exposes `WebhookMetadata#shop` as a verified field alongside an HMAC-checked request. A host application built against this API (reasonably) assumes that if `Registry.process` didn't raise `InvalidWebhookError`, then `data.shop` is trustworthy. An attacker can leverage this to trigger cross-tenant side effects (data deletion/redaction, order/customer record manipulation, state changes) attributed to a shop they do not own — this is cross-tenant access, rated Critical per the given impact taxonomy.

### Likelihood Explanation
Requires only an unprivileged attacker who can install the target app on any shop they control (a normal, publicly available action for public apps) and the ability to send arbitrary HTTP requests with custom headers to the host's known webhook endpoint (typically discoverable from the app's registered webhook URL pattern). No access token, `client_secret`, or privileged account is required — only the app's shared webhook HMAC scheme, which is inherent to how this gem validates requests.

### Recommendation
`Request#to_signable_string`/`HmacValidator` alone cannot authenticate the shop; the library should not present `shop` (or `topic`/`webhook_id`) as trusted fields based solely on body HMAC validation. At minimum, document that `WebhookMetadata#shop` is unauthenticated header data and require/provide a mechanism for hosts to cross-check `shop` against their own registered/installed-shop list before acting on the payload, or extend the verification to include the shop header as part of an out-of-band, per-tenant check (e.g., confirm the shop has an active session/access token before trusting the webhook).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a legitimate webhook, e.g. `orders/create`, to their own registered `path`. They capture the raw POST body and the `X-Shopify-Hmac-Sha256` header value (valid under the app's shared `client_secret`).
2. Attacker sends a new HTTP request to the host app's webhook endpoint with:
   - Same raw body and `X-Shopify-Hmac-Sha256` header (unchanged, still valid).
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged).
   - `X-Shopify-Topic: orders/create` (unchanged or forged).
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` accepts it [8](#0-7) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes the HMAC over `raw_body` [6](#0-5) .
4. `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", ...)` is passed to the host's registered handler, which processes/records the event as belonging to `victim-shop.myshopify.com` even though it never sent this webhook [7](#0-6) .

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
