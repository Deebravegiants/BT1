### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by the HMAC signature, allowing cross-tenant event spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers when dispatching to the registered handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC exclusively against that signable string [2](#0-1) . Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) with no cryptographic binding to those header values [3](#0-2) .

`Registry.process` validates the HMAC and, if it passes, immediately builds `WebhookMetadata` from these unauthenticated header fields and hands it to the app's handler as the trusted tenant/topic identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [4](#0-3) . `WebhookMetadata.shop` is a plain `String` constant with no further verification [5](#0-4) .

The binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic ‖ webhook_id)`, i.e. the tenant/topic identity used by the handler should be covered by the same signature that authenticates the request. In this code, the equality actually enforced is only `hmac == HMAC(secret, body)`; `shop`, `topic`, and `webhook_id` are asserted, not verified. Any caller who possesses one valid `(body, hmac)` pair — which they legitimately obtain for their own store's genuine webhook deliveries — can replay that exact body/hmac pair to the app's public webhook endpoint while substituting arbitrary values for `shop-domain`, `topic`, and `webhook-id` headers. `HmacValidator.validate` still returns `true` because it only checks the body, and the forged headers flow straight through to the handler as if Shopify itself asserted them.

### Impact Explanation
This breaks the tenant-authentication boundary the gem is documented to provide: apps rely on `WebhookMetadata#shop` from `Registry.process` as the authenticated store identity for dispatching data (e.g., writing to per-shop records, triggering per-shop side effects, GDPR redaction routines for `MANDATORY_TOPICS` such as `shop/redact` or `customers/redact`). An attacker who owns one shop with the app installed can capture a legitimate webhook payload/HMAC pair from their own store and replay it with a different `shop-domain` header, causing the app to process/attribute that event as coming from a different, victim shop — a cross-tenant confusion via a header the gem exposes as if it were authenticated.

### Likelihood Explanation
Exploitation only requires normal, unprivileged access to a store that has the target app installed (any merchant can install most public apps) plus the ability to observe one real webhook delivery to their own endpoint (webhook payloads are typically delivered over plaintext-inspectable HTTP to the app's own server, or can be triggered by the attacker performing an action on their own store that fires a webhook). No `api_secret_key`, access token, or privileged credential is needed — only a captured `(body, hmac)` pair from a webhook that was legitimately sent to the attacker's own shop.

### Recommendation
Include the identity-bearing header values (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the payload before trusting them in `WebhookMetadata`. At minimum, document/require that consuming apps must independently verify `data.shop` against the topic-specific record referenced in `data.body` rather than trusting the header-derived value as an authenticated tenant identifier.

### Proof of Concept
1. Install the vulnerable app on Shop A (attacker-controlled) and capture one legitimate webhook delivery to the app's public webhook endpoint, e.g.:
```
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid-hmac-for-body>
x-shopify-shop-domain: shop-a.myshopify.com
x-shopify-webhook-id: <id>
Body: {"id":123, ...}
```
2. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally the topic/webhook-id).
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (no validation on their values) [6](#0-5) , and `HmacValidator.validate` still returns `true` since only the body is checked [2](#0-1) .
4. `Registry.process` dispatches to the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` [4](#0-3) , causing the app to act as though the event genuinely originated from the victim shop.

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
