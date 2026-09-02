Confirmed finding: the docs explicitly state `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and then hands the handler a `shop` field taken straight from the `shop-domain` header [2](#0-1) , yet the HMAC that "verifies" the request only ever covers the raw body.

### Title
Webhook `shop` identity is not bound by the HMAC that "verifies" the request — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , so `Utils::HmacValidator.validate(request)` only proves that the *body* bytes were signed by Shopify — it says nothing about the `shop-domain`, `topic`, or `webhook-id` headers [4](#0-3) . `Registry.process` nonetheless treats a passing HMAC check as proof the whole request "did indeed come from Shopify" for that shop, and forwards the unauthenticated `shop` header value straight to the app's handler as the tenant identifier [5](#0-4) .

### Finding Description
The identity binding that should hold is: `hmac(raw_body, api_secret_key) valid ⇒ (raw_body, shop, topic, webhook_id) are all authentic for that shop`. In reality the equality only covers `raw_body`:

- `hmac` is computed from the `hmac-sha256` header alone [6](#0-5) .
- `to_signable_string` is exactly `@raw_body`, excluding every header [3](#0-2) .
- `shop`, `topic`, and `webhook_id` are read directly from attacker-controllable HTTP headers with no cross-check against the verified body [7](#0-6) .
- `Registry.process` validates the HMAC, then immediately constructs `WebhookMetadata` using `request.shop` (the header) as the tenant identity handed to the app's handler [8](#0-7) .

This is the same bug class as the C4 report: a compound identity check ("HMAC valid" + "topic/shop used downstream") is treated as one atomic guarantee, but the second part (`shop`) is never actually covered by the cryptographic proof used for the first part.

### Impact Explanation
Any party capable of receiving one genuine, HMAC-signed webhook body from Shopify (e.g., an unprivileged merchant who installs the app on their own store and captures a webhook delivery, or any other actor able to obtain a body+signature pair for *any* shop/topic combination) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` (and `topic`/`webhook_id`) header. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will hand the host app a `WebhookMetadata` claiming the payload originated from a different, victim shop [9](#0-8) . If the host app trusts `data.shop` (exactly as the gem's own documentation instructs developers to do [10](#0-9) ) to select which tenant's session/data to mutate, this enables cross-tenant data injection/corruption — attacker-controlled webhook content processed under a victim shop's identity.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus a single legitimately-signed webhook body (obtainable by installing the app on any store, which is an unprivileged action). No access to `api_secret_key`, access tokens, or the victim's credentials is needed, satisfying the unprivileged-attacker bar.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated — either by including these fields in the signed string (as Shopify actually intends the header value only to be trusted after body-HMAC verification, so the gem should additionally verify that `shop` corresponds to a shop with a known/registered subscription/session for that webhook id) or by requiring host apps to cross-check `data.shop` against an independent, already-authenticated record (e.g., a stored webhook subscription mapped to a specific shop) before trusting it. At minimum, update `docs/usage/webhooks.md` to state clearly that `data.shop` is unauthenticated header data and must not be trusted as a tenant selector without additional verification.

### Proof of Concept
1. App receives a legitimate Shopify webhook for `topic: orders/create`, `shop-domain: attacker-shop.myshopify.com`, with a valid `x-shopify-hmac-sha256` computed over the raw body.
2. Attacker replays the identical raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` accepts the request (all required headers present) [11](#0-10) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `raw_body` [12](#0-11) .
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's body content, despite the payload never having been signed for, or sent by, that shop [9](#0-8) .

### Citations

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

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
