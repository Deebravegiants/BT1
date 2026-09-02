Found it: `Webhooks::Request#shop` and `#topic` and `#webhook_id` are read directly from HTTP headers and are **not part of the HMAC-signed data**. The HMAC in this gem only covers the raw request body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` come from the `shopify-*` / `x-shopify-*` headers, which are attacker-controllable bytes verified separately (or not at all) from the bytes that are actually HMAC-verified.

### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` sourced from unauthenticated HTTP headers, while `Registry.process` only verifies the HMAC over the raw body via `Utils::HmacValidator.validate(request)`, whose signable string is `to_signable_string` = `@raw_body` [1](#0-0) . This breaks the identity binding: `bytes verified` (raw body) != `bytes acted on` (headers used for shop/topic dispatch).

### Finding Description
`Registry.process` calls `Utils::HmacValidator.validate(request)` before dispatching, which only confirms that the HMAC signature matches the request body [2](#0-1) . The `hmac` getter decodes `hmac-sha256`/`x-shopify-hmac-sha256` header bytes and compares them against `HMAC(body, secret)` [3](#0-2) . However, `shop`, `topic`, and `webhook_id`, which are handed unverified to the app's `handler.handle` call as `WebhookMetadata`, are read straight from `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers [4](#0-3) [5](#0-4) . Since the HMAC only signs `@raw_body`, none of these header values are cryptographically bound to the signature. If an app deployment forwards or proxies a legitimately-signed webhook body while an intermediary (load balancer, reverse proxy, CDN, or even the app's own routing layer merging headers from multiple sources) allows attacker-influenced or duplicate `shopify-shop-domain` / `shopify-topic` headers to reach this constructor, the gem will process the request under an attacker-chosen `shop` and `topic` identity even though the HMAC only proves the body's integrity, not the header's authenticity — an equality break of `shop verified == shop acted on`.

### Impact Explanation
This is High severity: a mismatch between the HMAC-verified data and the tenant identifier used for dispatch (`shop`) can lead to cross-tenant confusion in the host application — the webhook handler will process business logic (e.g., data deletion, order fulfillment sync, GDPR redact events) attributing it to a `shop` value never covered by the signature, `Registry.process` -> `WebhookMetadata` -> `handler.handle(data:)` [6](#0-5) .

### Likelihood Explanation
Requires a network position capable of injecting or duplicating the `shopify-shop-domain`/`shopify-topic` headers alongside a validly-signed body of a webhook the attacker previously received for their own store (e.g. header-smuggling through a misconfigured proxy in front of the Rack app). This is a real, though not trivially internet-reachable, precondition — it does not require the app's `client_secret` or an access token, only control over request headers reaching this constructor, which is plausible in multi-tenant/proxied deployments.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them, e.g., by having `Utils::HmacValidator` validate a canonicalized string containing headers + body rather than body alone), so the identity fields used for dispatch are provably the same bytes Shopify signed.

### Proof of Concept
1. Attacker with a real store receives a legitimately signed webhook for `shop=attacker-shop.myshopify.com`, topic `orders/create`, with valid `X-Shopify-Hmac-Sha256` computed over the body.
2. Attacker replays this exact body/HMAC to the victim app's webhook endpoint but manipulates/duplicates the `shopify-shop-domain` and `shopify-topic` headers (via a proxy that doesn't strip attacker-supplied headers, or an app that merges headers from multiple sources) to `victim-shop.myshopify.com` / `customers/redact`.
3. `Webhooks::Request.new(raw_body:, headers:)` stores headers as-is [7](#0-6) ; `Registry.process` verifies only the body's HMAC, which still matches because the body was untouched, then dispatches `handler.handle` with the attacker-chosen `shop`/`topic` [5](#0-4) .
4. The host application processes the webhook as if it legitimately came from `victim-shop.myshopify.com` for `customers/redact`, even though only the body (not the shop/topic) was ever HMAC-verified.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
