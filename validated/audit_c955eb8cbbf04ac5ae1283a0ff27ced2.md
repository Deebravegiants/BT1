### Title
Webhook shop attribution is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with the app's `api_secret_key` [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Registry.process` are all read straight from unauthenticated HTTP headers (`shopify-shop-domain`, etc.) [3](#0-2)  and are never included in the signable string that the HMAC covers.

### Finding Description
`Registry.process` does:
```
raise ... unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [4](#0-3) 

The identity binding that should hold is: `shop-domain header == shop that produced/authorized the signed body`. However, the HMAC only binds `secret == HMAC(raw_body)` [5](#0-4) ; it says nothing about which shop the body belongs to. Because a single app has one `api_secret_key` shared across every installing shop, a valid `(raw_body, hmac)` pair captured from a webhook delivered for Shop A remains cryptographically valid no matter what value is placed in the `shopify-shop-domain` header. An attacker who legitimately installs the app on Shop A (an "unprivileged internet user" with respect to any other tenant) can capture one of their own real webhook deliveries and replay the identical body/HMAC to the app's webhook endpoint with the `shopify-shop-domain` header changed to Shop B. `HmacValidator.validate` still returns `true` (the body/secret pair is genuine), and `Registry.process` will hand the host application a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` while the body content actually belongs to Shop A [6](#0-5) .

The gem's own documentation reinforces the false assumption that HMAC validation proves shop-scoped authenticity ("This will verify the request did indeed come from Shopify") [7](#0-6) , and the example handler dispatches directly on `data.shop` to decide which tenant's records to update [8](#0-7) , so any host app following the documented pattern inherits the cross-tenant confusion.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to guarantee for webhook processing: a request whose payload is genuinely signed for one shop can be attributed to a different shop merely by changing an unauthenticated header, letting a malicious merchant inject or replay data attributed to another store (`shop` value drives which tenant record the host app updates). This matches the "Critical - cross-tenant access" impact category, since the shop identity used to route/persist webhook data is not bound to the cryptographic proof of authenticity.

### Likelihood Explanation
Likelihood is moderate-to-high for any app: the attacker only needs their own legitimate install (a normal unprivileged tenant) to capture a valid `(body, hmac)` pair, and can then POST it to the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header — no access token, secret, or elevated privilege is required, only network access to the app's webhook callback URL.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable content, or independently validate that `request.shop` corresponds to a shop with an active session/installation and that the specific `webhook_id` hasn't already been attributed to a different shop, before invoking the handler in `Registry.process`.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com`; attacker controls that store and can observe/log Shopify webhook deliveries to their own endpoint (raw body + `shopify-hmac-sha256` + `shopify-shop-domain: shop-a.myshopify.com`).
2. Attacker resends the identical `raw_body`/`hmac` pair to the app's webhook endpoint but sets `shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally [9](#0-8) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes HMAC over `raw_body` with the app-wide `api_secret_key` [10](#0-9) .
4. `handler.handle` is invoked with `WebhookMetadata(shop: "shop-b.myshopify.com", body: <shop-a's data>, ...)`, causing the host app to process/store Shop A's data under Shop B's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
