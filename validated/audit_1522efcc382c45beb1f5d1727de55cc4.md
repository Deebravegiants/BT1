### Title
Webhook `shop` (and `topic`) identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) and event `topic` exclusively from HTTP headers (`shopify-shop-domain`/`x-shopify-shop-domain`, `shopify-topic`/`x-shopify-topic`), while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body via `to_signable_string`, which returns `@raw_body` and nothing else. [1](#0-0) [2](#0-1) 
This breaks the binding: `shop attributed to a webhook == shop that actually generated it`. The HMAC proves the body is untampered and came from an entity with the API secret, but it proves nothing about which shop the `shop-domain` header refers to.

### Finding Description
`Registry.process` validates the webhook solely with `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` — this is the raw body only. [3](#0-2) [4](#0-3) 
After this single check passes, `request.shop` and `request.topic` — both read straight from headers with no cryptographic binding to the body or to the verified HMAC — are handed to the app's handler as trusted identity data: [5](#0-4) 
The documentation instructs integrators to treat `data.shop` as the authoritative "shop domain of the webhook" for dispatching to per-tenant logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), reinforcing that this field is meant to carry trusted tenant identity. [6](#0-5) 

Because the HMAC only signs the body, an attacker who has legitimate control of *any* shop that can generate a real, correctly-signed webhook (e.g. their own installed test store, for a topic like `orders/create`) can capture a genuine `(body, hmac)` pair signed with the app's real secret, then replay it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain (and/or `shopify-topic` rewritten). `HmacValidator.validate` still succeeds because it only re-derives the signature from the unmodified body. `Registry.process` will then dispatch to the handler with `shop: <victim-shop>` — misattributing attacker-controlled webhook content to a different tenant.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem lets an attacker who controls one authenticated webhook source (their own shop, with real HMAC secret access is not even required — only a captured, validly-signed payload from any topic/shop they can trigger) forge which merchant a webhook body/topic is attributed to. Any host application that (as documented) keys per-shop session/data lookups or queued jobs off `data.shop` from this gem will process attacker-supplied webhook content under an arbitrary shop identity of the attacker's choosing, i.e., cross-tenant access/injection. This matches the Critical impact category "cross-tenant access" in the rules, since the gem's own `process`/`WebhookMetadata` pipeline is what performs the unguarded identity attribution.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker must be able to obtain at least one genuinely-signed `(body, hmac)` pair for the target app (e.g. by installing the app on a store they control and letting Shopify send a real webhook, which is a normal, unprivileged action available to anyone who can install a Shopify app), and must be able to reach the app's webhook HTTP endpoint directly with modified headers (not through Shopify's own delivery, but as a raw HTTP POST, which is how these endpoints are exposed to the internet). No access token, `client_secret`, or privileged credentials of the target shop are needed — only network access to the app's public webhook endpoint and a self-generated legitimate webhook payload/signature pair from any topic reachable to the attacker.

### Recommendation
Bind the shop/topic identity into the HMAC-verified material, or otherwise cryptographically/authoritatively verify `request.shop` before trusting it:
- At minimum, document/enforce that `request.shop` must be cross-checked by the host application against an app-side registry of shops that are known to have this exact webhook topic registered (with matching `webhook_id`), rather than presenting `shop` as an already-trusted attribute in `WebhookMetadata`.
- Prefer including `shop`/`topic`/`webhook_id` in the signable string used for HMAC verification (if Shopify's delivery guarantees allow it) so header-only tampering cannot pass validation.
- At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop`/`data.topic` are not covered by the HMAC and must not be used as sole tenant-identity input for security-sensitive dispatch.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering a real webhook (e.g. `orders/create`) which Shopify sends to the app with a valid body and `x-shopify-hmac-sha256` signature computed by Shopify using the app's real `api_secret_key`.
2. Attacker captures this raw request: `raw_body` (e.g. `{"id":1,...}`) and its valid HMAC.
3. Attacker replays the exact same `raw_body` + HMAC header to the app's public webhook endpoint, but changes:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - (optionally) `x-shopify-topic` to any topic the app has registered.
4. `ShopifyAPI::Webhooks::Request.new` accepts the headers (only presence, not content, of `shop-domain`/`topic` is checked). [7](#0-6) 
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`@raw_body`, unchanged) and succeeds. [8](#0-7) 
6. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `shop` is now `victim-shop.myshopify.com` despite the body originating from the attacker's own store. [5](#0-4) 
7. Any host application logic that uses `data.shop` to select which merchant's records/session to update (as the gem's own documentation recommends) now operates on attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-29)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
