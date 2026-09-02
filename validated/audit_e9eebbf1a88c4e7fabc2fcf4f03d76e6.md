I have sufficient evidence to confirm the vulnerability.

### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted by `Webhooks::Registry.process` without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , and `Utils::HmacValidator.validate` only verifies that this body is unmodified relative to the app's `client_secret` [2](#0-1) . The `shop`, `topic`, and `webhook_id` values, however, are read straight from unauthenticated HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`) [3](#0-2)  and are handed directly to the host application's handler as trusted tenant/topic identity via `WebhookMetadata` [4](#0-3) [5](#0-4) .

### Finding Description
The identity binding that should hold is: `shop header == shop bound inside the HMAC-signed payload`. Instead, `Utils::HmacValidator.validate` only proves "bytes verified == bytes parsed" for the request body — it recomputes the HMAC over `@raw_body` [1](#0-0)  and compares it in constant time to the received signature [6](#0-5) . It never folds `shop-domain`, `topic`, or `webhook-id` into the signable string, so those header values are never covered by the signature.

`Registry.process` treats `Utils::HmacValidator.validate(request)` as sufficient proof of authenticity for the entire request, then unconditionally forwards `request.shop`, `request.topic`, and `request.webhook_id` — pulled purely from headers — to the registered handler [4](#0-3) . Because the headers sit outside the HMAC's protection, any party who has ever obtained one valid `(body, hmac)` pair for the app's shared secret (e.g., by installing the app on their own shop and receiving one legitimate webhook) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` header values. `Utils::HmacValidator.validate` will still return `true` because the signed bytes (body) are unchanged, but the host application will process the payload as though it originated from a different shop or topic than it actually did.

### Impact Explanation
This breaks the tenant-identity binding the host application relies on to route webhook data per-shop. An attacker can make the app process/store the replayed webhook body as belonging to a victim shop domain of their choosing (cross-tenant confusion), or replay it under a different `topic` to trigger unintended handler logic (e.g., feeding `orders/create` data into a `customers/redact` handler if the body happens to parse for both). Given the gem is what host apps use to authenticate and route inbound Shopify webhooks, this is a cross-tenant identity/authenticity issue matching the Critical "cross-tenant access" impact category, since it lets one shop's traffic be misattributed to another shop without possessing that shop's credentials.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop to receive at least one legitimate webhook (any topic) signed with the app's shared secret, and (2) sending a crafted HTTP POST directly to the app's public webhook endpoint with the captured raw body/HMAC pair and forged Shopify headers. No access to the app's `client_secret`, access tokens, or victim credentials is required — this is achievable by any unprivileged internet user/app installer.

### Recommendation
Bind the header-derived identity fields into the signed payload verification. Concretely, extend `Utils::VerifiableQuery`/`Request#to_signable_string` (or add a dedicated check in `Registry.process`) so that `shop`, `topic`, and `webhook_id` are either: (a) included in the HMAC-signable string used by `Utils::HmacValidator.validate`, or (b) cross-checked against a shop/session already known to the host app (e.g., verifying `request.shop` corresponds to a shop with a stored, previously-authenticated session) before invoking the handler in `Registry.process`.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture one legitimate webhook delivery, e.g. `raw_body = '{"id":1}'` with header `x-shopify-hmac-sha256: <valid hmac of raw_body>`.
2. Craft a POST to the app's webhook endpoint reusing that exact `raw_body` and `hmac` header, but set `x-shopify-shop-domain: victim.myshopify.com` and/or `x-shopify-topic: shop/redact`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged headers [7](#0-6) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because only `raw_body` is checked [8](#0-7) .
4. The handler receives `WebhookMetadata.new(topic: "shop/redact", shop: "victim.myshopify.com", body: ..., ...)` and processes it as an authentic event for `victim.myshopify.com`, even though the payload was never actually signed for that shop or topic.

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
