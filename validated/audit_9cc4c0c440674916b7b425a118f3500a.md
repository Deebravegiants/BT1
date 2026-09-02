I have sufficient evidence to confirm the finding. The core issue is confirmed by:

1. `Utils::VerifiableQuery#to_signable_string` for `Webhooks::Request` returns only `@raw_body` [1](#0-0) 
2. `HmacValidator.validate` / `validate_signature` computes the HMAC only over `to_signable_string` (the body), never over headers [2](#0-1) 
3. `Registry.process` raises only on HMAC failure, then immediately trusts `request.topic`/`request.shop` (parsed from unauthenticated headers) to build `WebhookMetadata` passed to the handler [3](#0-2) 
4. `Request#shop` is read directly from the `shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed body [4](#0-3) 
5. `WebhookMetadata.shop` is a plain `String` const with no binding to the HMAC-verified payload [5](#0-4) 
6. The gem's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify," which is inaccurate for the shop-domain claim [6](#0-5) 

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator` validates the HMAC exclusively against that body. The `shop-domain` (and `topic`, `webhook-id`, `api-version`) headers are never included in the signed content, yet `Registry.process` treats `request.shop` as an authenticated tenant identifier and hands it directly to the app's webhook handler via `WebhookMetadata`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def to_signable_string
  @raw_body
end
``` [7](#0-6) 

`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC using `OpenSSL.secure_compare` [2](#0-1) . Since `to_signable_string` is only the body, the signature is a function of the body and the app's single shared `api_secret_key` — it says nothing about which shop the request claims to be from.

`Registry.process` then does:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

`request.shop` is read straight from the `shop-domain`/`x-shopify-shop-domain` header [4](#0-3) , with no cross-check that this header is consistent with any signed value.

The identity binding that should hold is: **shop claimed in `WebhookMetadata.shop` == shop cryptographically bound by the HMAC**. In this gem it is instead: `WebhookMetadata.shop == arbitrary attacker-controlled header value`, because the HMAC secret (`api_secret_key`) is shared across all shops that installed the app — it is not per-shop. Any user who installs the app on their own store legitimately receives real `(body, hmac)` pairs signed with the app's secret. That user can then replay the exact same valid `body`/`hmac` pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (the body/hmac pair is genuinely valid), and `Registry.process` passes the attacker-chosen `shop` value straight to the handler as if Shopify itself had asserted it.

Downstream host applications (per this gem's own documented pattern, see `docs/usage/webhooks.md`) use `data.shop` to look up the merchant's session/access token and perform actions on that merchant's behalf — e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [8](#0-7) . Since the gem provides no way to distinguish an authentic shop claim from a forged one, any handler built on top of this API inherits the cross-tenant confusion.

### Impact Explanation
This breaks the tenant boundary: an attacker with a legitimate app installation on shop A can make the app believe an arbitrary Shopify-shaped payload came from shop B (any known/guessed `*.myshopify.com` domain that also installed the app). Because the gem's documentation explicitly asserts that `Registry.process` "will verify the request did indeed come from Shopify," downstream integrators reasonably treat `WebhookMetadata.shop` as trustworthy, so their handlers (which look up shop B's session/access token by that shop string) are misled into processing attacker-supplied body content under shop B's identity — a cross-tenant integrity violation of the app's webhook data pipeline.

### Likelihood Explanation
Likelihood is high for any real-world usage of this gem's webhook feature: the vulnerable code path (`Registry.process`) is the only documented way to consume http webhooks, no additional configuration disables it, and the only prerequisite is possessing one valid `(raw_body, hmac)` pair signed with the app's shared secret — trivially obtained by any user who installs the app and inspects the webhook the app receives from their own store.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the signed content that `HmacValidator` verifies, or otherwise cryptographically bind `request.shop` to the signature (e.g., verify shop via a separate authenticated channel such as looking up the registered webhook by `webhook_id` through the Admin API, rather than trusting the header). At minimum, `Request#to_signable_string` should not silently omit header fields (`shop`, `topic`, `webhook_id`, `api_version`) that are subsequently treated as authenticated in `WebhookMetadata`, and the documentation claim that `process` "verifies the request did indeed come from Shopify" should be corrected to clarify that only the body is verified, not the claimed shop domain.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com`, triggers an event (e.g., creates an order) and captures the resulting legitimate webhook HTTP request sent by Shopify to the app, including its `x-shopify-hmac-sha256` header and raw JSON body.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint, keeping the exact `raw_body` and `x-shopify-hmac-sha256` value unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com` and any desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses these headers [9](#0-8) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/hmac pair was genuinely produced by Shopify with the app's shared secret [10](#0-9) .
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order data>, ...)` and, following the gem's documented pattern, performs shop-scoped actions (session lookup, background job dispatch, etc.) under the victim shop's identity using attacker-controlled body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L24-29)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
