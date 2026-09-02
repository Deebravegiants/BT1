Confirmed: `Request#to_signable_string` (used by `HmacValidator.validate`) signs only `@raw_body` — the `shop` (from `shopify-shop-domain` header), `topic`, `api-version`, and `webhook-id` fields are read directly from HTTP headers and are never included in the HMAC-covered bytes.### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `HmacValidator.validate` authenticates the body bytes but never authenticates the `shopify-shop-domain` header. `Registry.process` nonetheless trusts that unauthenticated header to populate `WebhookMetadata#shop`, which is the value apps use to attribute the webhook to a tenant. This breaks the identity binding `shop_authenticated == shop_acted_on`, analogous to the Sherlock report where a field influencing the outcome (`closePrice`) was checked under one condition set but the wrong values were bound together — here the signed bytes (body) and the acted-upon identity field (`shop`) are decoupled.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 
`to_signable_string` returns `@raw_body` only — none of the `shop`, `topic`, `api_version`, or `webhook_id` header-derived accessors are part of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string`: [3](#0-2) 

`Registry.process` gates on this HMAC check, then immediately trusts `request.shop` (the raw `shopify-shop-domain`/`x-shopify-shop-domain` header) to build `WebhookMetadata` passed to the app's handler: [4](#0-3) 

`WebhookMetadata#shop` is documented as "The shop domain of the webhook" and apps are expected to key business logic (e.g. per-tenant job dispatch) off it: [5](#0-4) [6](#0-5) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, and the HMAC is computed only from the raw body, an unprivileged actor who has legitimately installed the app on their own shop can obtain a genuinely-signed `(raw_body, hmac)` pair from Shopify. They can then replay that exact pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the shop header), so `Registry.process` calls the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`.

### Impact Explanation
This is a cross-tenant identity-binding failure: the byte range verified by HMAC (body only) does not equal the byte range acted upon (body + shop header). Any host app that persists or acts on `data.shop` (as the documented usage pattern explicitly recommends: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be tricked into attributing attacker-controlled webhook content to an arbitrary victim shop it hosts, without needing the victim's access token or the app's `client_secret`. This matches the Critical "cross-tenant access" category in scope, since it lets one tenant's legitimately-received webhook be relabeled as belonging to another tenant.

### Likelihood Explanation
Likelihood is constrained by the requirement that the attacker have their own legitimate installation of the app (any merchant can install most public Shopify apps) and knowledge of a topic they can trigger for their own shop (e.g. `orders/create` by placing an order in their own store), plus the target app relying on `data.shop` without independently re-verifying it via an authenticated session or the GraphQL Admin API. This is a realistic, unprivileged, low-cost attack path requiring no leaked credentials, TLS interception, or social engineering — only normal use of the app as an installer.

### Recommendation
Include the shop domain (and ideally topic/webhook_id) in the HMAC-covered bytes, or independently verify the `shopify-shop-domain` header against a value obtained through an authenticated channel (e.g., cross-check against the shop associated with the stored offline session/access token before dispatching to the handler) rather than trusting the raw header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook topic the app subscribes to (e.g. creates an order), causing Shopify to POST a genuinely-signed request: headers include `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON body.
3. Attacker captures the raw body and HMAC header, then replays them to the same app's webhook endpoint but rewrites the `shopify-shop-domain` header to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `HmacValidator.validate` recomputes HMAC over `@raw_body` only and it matches, so `Registry.process` calls the app's `WebhookHandler#handle` with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)`.
5. Any app logic that trusts `data.shop` (per the documented pattern) now performs actions or persists data under the victim shop's tenant using attacker-supplied content.

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
