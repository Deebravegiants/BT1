### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from an HTTP header, but the HMAC that `Utils::HmacValidator` verifies only covers the raw request body. Any attacker who can obtain one valid `(body, hmac)` pair for the app (trivially available to any merchant who has legitimately installed the app, since the webhook secret is the app's single shared `client_secret`, not a per-shop secret) can replay that body with a forged `shop-domain` header pointing at a different, victim shop, and the signature check will still pass.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight out of unauthenticated headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the `hmac` header value, using the app-wide `Context.api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` treats a passing HMAC check as authorization to trust the entire `Request` object, including `request.shop`, and forwards it unchanged to the app's handler as the tenant identity for the event: [4](#0-3) 

Because Shopify signs app webhooks with the single app-level `client_secret` (identical for every shop that has installed the app) rather than a per-shop secret, and because that secret is not scoped to a specific `shop-domain`/`topic`/`webhook-id`, a valid `(body, hmac)` pair generated for shop A's webhook is also a valid `(body, hmac)` pair when replayed with a different `shop-domain` header claiming to be shop B. The gem has no mechanism to detect this substitution — the equality the code implicitly (and incorrectly) assumes is:

`shop authenticated by HMAC == shop claimed in the shop-domain header`

but in reality the HMAC only certifies `body authenticated by HMAC == body bytes received`; the `shop`/`topic`/`webhook_id` fields are never part of what's signed.

### Impact Explanation
Any merchant who installs the app on their own store (an "unprivileged internet user" relative to other merchants of the same app) can trigger events in their own shop (e.g. create an order/product) to obtain a legitimate `raw_body` + `hmac` pair signed with the app's shared secret, then replay that exact body to the app's webhook endpoint while spoofing the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header to name a victim shop. Because `Registry.process` only gates on `HmacValidator.validate`, which never inspects `shop`, the forged request is accepted and dispatched to the handler with `WebhookMetadata#shop` set to the victim shop but attacker-controlled body content. Any host application that uses `WebhookMetadata#shop` to scope data writes (the intended and documented usage pattern) can be made to apply attacker-chosen webhook data to another tenant's records — a cross-tenant data integrity/access issue.

### Likelihood Explanation
The prerequisite — being a legitimate, unprivileged merchant of the same app who can capture one valid signed webhook body for their own shop — is trivially satisfiable and requires no credentials belonging to the victim, the app's `client_secret`, or any privileged access. The replay itself is a simple HTTP request with a modified header.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signed payload verification (e.g., bind them into `to_signable_string`, or require the host application to additionally verify that `request.shop` matches the shop the webhook subscription was registered against) so that the HMAC check certifies the tenant/topic identity, not just the raw body bytes.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker triggers e.g. an `orders/create` event and captures the resulting webhook `raw_body` and `shopify-hmac-sha256` value sent by Shopify (both are visible to the receiving app's own logs/network since it is the attacker's own shop).
2. Attacker sends a POST to the app's webhook endpoint with:
   - `shopify-hmac-sha256`: the captured valid HMAC
   - body: the captured `raw_body` (attacker fully controls its contents since it's their own shop's data)
   - `shopify-shop-domain`: `victim-shop.myshopify.com`
   - `shopify-topic`: unchanged or forged
3. `ShopifyAPI::Webhooks::Request.new` builds the request object from these headers/body: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body's HMAC against `Context.api_secret_key`, matching the value computed in step 1: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` and the attacker's crafted body, even though this data never originated from `victim-shop`: [7](#0-6)

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
