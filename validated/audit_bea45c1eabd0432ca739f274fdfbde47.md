### Title
Webhook HMAC only signs the request body, so the `shop`, `topic`, and `webhook_id` headers are unauthenticated and can be forged for cross-tenant webhook injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content for HMAC verification from the raw body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers and passed on to the app's webhook handler as trusted metadata.

### Finding Description
`Registry.process` accepts a `Request` and only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler: [1](#0-0) 

`HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field of the object: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` are pulled directly from HTTP headers that are never included in the signed string: [3](#0-2) 

This means the equality the code implicitly claims to enforce — `hmac(raw_body) == hmac(raw_body, shop, topic, webhook_id)` — does not hold; the signature only binds `raw_body`, not the identity fields (`shop`, `topic`, `webhook_id`) that the app uses to route and attribute the webhook. `handler.handle` is called with a `WebhookMetadata` built directly from these unauthenticated headers: [4](#0-3) [5](#0-4) 

Since `Context.api_secret_key` (the app's client secret) is a single shared value across every shop that has the app installed, any unprivileged user who installs the app on their own (e.g. free development) store legitimately receives real webhook deliveries with a valid `(raw_body, hmac)` pair signed with that same secret. The attacker can then replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header with a victim shop's domain or a different topic. `HmacValidator.validate` will still pass because the signature check never inspects those headers, so the forged request is accepted as if it genuinely originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC check is supposed to enforce: `Auth.validate` for webhooks == `Utils::HmacValidator.validate` (body-only), but consumers of this gem treat `WebhookMetadata#shop` as an authenticated tenant identifier. An attacker controlling one shop can inject webhook events falsely attributed to another shop into the host application, i.e., cross-tenant data injection. This matches the "Critical - cross-tenant access" impact bucket, since the identity binding (`shop` field acted upon) is not covered by the HMAC that is supposed to authenticate the whole message.

### Likelihood Explanation
Likelihood is moderate-to-high for any real-world app: obtaining a legitimate `(raw_body, hmac)` sample only requires installing the app once on an attacker-controlled/dev store (no special privilege, no leaked secret needed), and the webhook HTTP endpoint is by definition internet-reachable. The main constraint is that the attacker must find or predict a `raw_body` whose content is useful/exploitable against the victim once shop-scoped, but for topics with generic or attacker-influenced bodies (e.g., `app/uninstalled`, `customers/data_request`, or webhooks where body content is attacker-influenced through their own shop's data) this is straightforward.

### Recommendation
Bind the identity/routing headers into the signed content instead of relying on the body alone. Since Shopify's own signature format only signs the raw body, the app-side mitigation should be to independently verify that the `shop` (and, if used for routing decisions, `topic`) in the webhook matches a shop/session actually known to and expected by the host application (e.g., cross-check against the app's list of installed/authorized shops) before trusting `WebhookMetadata`, and to document this requirement clearly for consumers of `ShopifyAPI::Webhooks::Registry.process`. At minimum, the gem should surface a warning/guard that `shop`/`topic`/`webhook_id` are not covered by the HMAC and must not be treated as verified without additional application-level checks.

### Proof of Concept
1. Install the target app on an attacker-owned development store `attacker-shop.myshopify.com`.
2. Trigger a webhook (e.g., `orders/create`) and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header — this is a valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`.
3. Replay the same POST body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally alter `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC, and `Registry.process` invokes the registered handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing the host app to process attacker-supplied data as if it came from the victim shop. [6](#0-5)

### Citations

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
