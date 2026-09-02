Based on my investigation, I found a concrete analog: the `shop` (and `topic`) identity fields used by `ShopifyAPI::Webhooks::Registry.process` are never covered by the HMAC signature that authenticates the webhook, exactly matching the report's "field acted on but not covered by the binding" pattern.

### Title
Webhook `shop-domain` and `topic` headers are trusted for dispatch/tenant identity but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  , so `Utils::HmacValidator.validate` only authenticates the JSON body, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers [2](#0-1) . Yet `Registry.process` uses `request.topic` to pick the handler and passes the unauthenticated `request.shop` straight into `WebhookMetadata`, which the host app is documented to use as the tenant identifier [3](#0-2) .

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, shop ‖ topic ‖ body)`, i.e. the authenticated bytes should cover every field the app acts on. Instead, the gem only computes `hmac == HMAC(secret, body)` [4](#0-3) , while `shop` and `topic` are read straight from HTTP headers with no cryptographic tie to the signature [5](#0-4) .

Because the same `Context.api_secret_key` signs webhooks for every shop that has installed the app, an unprivileged internet user who installs the app on their own store legitimately receives HMAC-valid webhook deliveries. That attacker can capture one such delivery (valid `body` + valid `hmac`) and replay it to the app's public webhook endpoint while altering only the `shop-domain` header to a victim shop's domain, and/or the `topic` header to a different registered topic. `HmacValidator.validate` still passes because it only checks `raw_body` against `hmac` [6](#0-5) , and `Registry.process` then hands the forged `shop` value straight to the handler [7](#0-6) .

The gem's own documentation reinforces the unsafe trust: it describes `data.shop` as simply "The shop domain of the webhook" and shows sample code keying business logic off it directly (`shop_domain: data.shop`) with no mention that this value is unauthenticated [8](#0-7) .

### Impact Explanation
This breaks the tenant identity binding (`shop` claimed == `shop` cryptographically authenticated). An attacker with no privileged credentials — only their own legitimate app installation — can make the host app process a webhook body attributed to a merchant they don't control (cross-tenant event injection), or dispatch a body to the wrong topic handler. Any app whose webhook handler uses `data.shop` to select which merchant's records to create/update/delete (as the gem's own docs suggest) is exposed to cross-tenant data corruption or business-logic confusion (e.g. faking `app/uninstalled`, `customers/redact`, or order-mutation events against a shop the attacker doesn't own).

### Likelihood Explanation
Reachable by any unprivileged internet user: no `api_secret_key`, access token, or privileged account is required beyond a normal, self-serve app installation on the attacker's own store to harvest one valid `(body, hmac)` pair. The victim's `shop-domain` is public information (the `.myshopify.com` handle). The only work is replaying an HTTP POST with a modified header, which any HTTP client can do.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable bytes (or otherwise independently verify the `shop-domain` header against the app's own list of shops that installed the app, and verify `topic` matches the subscription actually registered) before dispatching to a handler in `ShopifyAPI::Webhooks::Registry.process`. At minimum, document prominently in `docs/usage/webhooks.md` that `data.shop` and `data.topic` are not covered by the HMAC and must be revalidated by the host app against known installed shops before being trusted.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and captures a real webhook delivery, e.g. headers `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-b64-hmac>`, body `{"id":1,...}`.
2. Attacker POSTs the identical body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [9](#0-8) .
4. `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `raw_body` [2](#0-1) , which is unchanged.
5. `Registry.process` invokes the registered `orders/create` handler with `data.shop == "victim-shop.myshopify.com"` [7](#0-6) , even though the payload never originated from that shop.

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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```
