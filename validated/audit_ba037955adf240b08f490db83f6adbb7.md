### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop as soon as `Utils::HmacValidator.validate(request)` passes, but the HMAC is computed only over the raw request body. The `shop` identity that is subsequently handed to the app's `WebhookHandler` comes from the `x-shopify-shop-domain` header, a value that is never included in the signed material. This breaks the intended binding `hmac_verified_bytes == identity_bytes_acted_on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC solely against `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` gates on that same HMAC check, then immediately trusts `request.shop` as the identity forwarded to the app-supplied handler: [4](#0-3) 

The resulting `WebhookMetadata#shop` is exactly what downstream apps are documented to use to route/attribute webhook data to a specific merchant: [5](#0-4) [6](#0-5) 

Because the header carrying shop identity is outside the HMAC's coverage, any two values `(raw_body, hmac)` that are valid for shop A remain valid if replayed with the `shop-domain` header changed to shop B. The gem provides no mechanism to detect this substitution — `Registry.process` only checks `Utils::HmacValidator.validate(request)` (body vs. secret) and never verifies that the claimed `shop` is the shop the payload was actually generated for.

### Impact Explanation
An attacker who operates (or has installed the app on) their own shop legitimately receives real webhook deliveries from Shopify for their own shop's events, each with a valid `(body, hmac)` pair signed with the app's `api_secret_key`. Because the header is unauthenticated, the attacker can replay that exact `(body, hmac)` pair directly to the app's public webhook endpoint while substituting `x-shopify-shop-domain` with a victim shop's domain. `Registry.process` will validate the HMAC (it is unchanged) and dispatch the payload to the app's handler tagged as originating from the victim shop. Any app logic that uses `WebhookMetadata#shop` to select which merchant's session/access token/state to act on (the documented and expected usage pattern) will act under a false tenant identity — this is a cross-tenant integrity/confusion issue reachable without knowledge of `api_secret_key`, `client_secret`, or any privileged account belonging to the victim.

### Likelihood Explanation
Any merchant who installs the app (an ordinary, unprivileged install — not a privileged operator of the app itself) obtains at least one legitimate `(body, hmac)` pair for their own shop by simply generating a webhook-triggering event (e.g., creating an order). No secret material needs to be recovered; the attacker only replays data they already legitimately possess with a modified header. The webhook endpoint is a public HTTP endpoint by design, so nothing prevents a direct POST outside of Shopify's delivery infrastructure.

### Recommendation
Bind the shop identity (and other routing-relevant headers such as `topic`/`webhook_id`) into the verified material, e.g., include the `x-shopify-shop-domain` header in the signable string used for HMAC computation, or independently verify that the shop in the payload/header matches an app-side expectation (e.g., cross-check the shop against a known/registered shop list, or use a per-shop secret/verification step) before trusting `WebhookMetadata#shop` for any state-mutating or data-returning operation.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a normal event (e.g., creates an order), causing Shopify to legitimately POST a webhook to the app with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-for-body>`, and some `raw_body`.
2. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value.
3. Attacker sends their own POST directly to the app's public webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only presence is checked, not header authenticity) — see the header presence check: [7](#0-6) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unmodified) body against the secret: [8](#0-7) 
6. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` set to `"victim-shop.myshopify.com"`, even though the payload never originated from that shop: [9](#0-8) 

Note: I was not able to fully verify Shopify's server-side webhook delivery behavior (i.e., whether Shopify's infrastructure independently constrains which `shop-domain` values can reach a given endpoint at the network layer) since that is outside this repository's index; the finding is scoped strictly to what this gem's own code validates and trusts.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L27-31)
```ruby
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

**File:** docs/usage/webhooks.md (L12-29)
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
    end
  end
end
```
