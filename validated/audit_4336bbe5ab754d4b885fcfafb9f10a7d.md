### Title
Webhook `shop` domain is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#shop` is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, while `HmacValidator.validate` only verifies the raw request body via `Request#to_signable_string`. The gem forwards this unauthenticated `shop` value straight into `WebhookMetadata` passed to the app's handler, so a valid HMAC (computed only over the body) never proves which shop the webhook is "for." Any holder of one validly-signed webhook body (e.g., an attacker who installed the app on their own store) can replay that body with a different `shop-domain` header pointed at a victim shop and have it accepted as authentic for that victim.

### Finding Description
The binding the app relies on is: `shop_attributed_to_webhook == shop_bound_by_HMAC`. In reality:

- `Request#hmac` and `Request#to_signable_string` only cover `@raw_body`: [1](#0-0) [2](#0-1) 

- `Request#shop` is taken from a plain header, never part of the signed bytes: [3](#0-2) 

- `HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e., the body) against `Context.api_secret_key`: [4](#0-3) 

- `Registry.process` validates the HMAC of the body, then unconditionally trusts `request.shop` (from the header) when constructing `WebhookMetadata` handed to the app's handler: [5](#0-4) [6](#0-5) 

Because the app's shared `api_secret_key` (client secret) is the same across every shop installation of the app, any merchant who has installed the app can generate their own arbitrary but validly-HMAC-signed webhook body (by causing any subscribed event on their own store, e.g. `orders/create`). They can then POST that exact `raw_body` + `hmac` header directly to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` passes because it only checks the body signature, and `Registry.process` calls the handler with `shop: <victim-shop>` and `body: <attacker-controlled>`.

The gem's own documented usage pattern explicitly routes this unauthenticated `shop` value into tenant-scoped processing: [7](#0-6) 

### Impact Explanation
This breaks the tenant isolation boundary the gem is expected to enforce for webhook processing: cross-tenant access/write. An attacker-controlled request, HMAC-valid solely because of the raw body, is attributed by the gem to a shop domain the attacker does not control. Any host application that follows the gem's documented pattern (using `data.shop` to select the tenant record to update, per the docs example `shop_domain: data.shop`) will apply attacker-influenced webhook data against a victim shop's data — satisfying the "cross-tenant access" criterion (Critical impact category).

### Likelihood Explanation
Medium-High. The prerequisite is only that the attacker be able to install the app on their own shop (any merchant can do this for public/embedded apps) and cause one webhook-eligible event on it — no leaked secrets, no access-token theft, and no privileged account are required. The `shop-domain` header is fully attacker-controlled on a direct HTTP POST to the app's webhook route, and the gem performs no binding check between it and the HMAC-verified body.

### Recommendation
Include the shop domain (and ideally other identifying headers such as `topic`/`webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind the `shop` claim to the payload before trusting it in `WebhookMetadata`. At minimum, `Registry.process` (or the host application) should cross-validate that the shop asserted in the header matches an actively-registered/expected shop for that specific webhook subscription (e.g., correlate against the webhook's known destination) rather than trusting an unauthenticated header value verbatim.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, obtaining the ability to trigger any subscribed webhook topic (e.g., `orders/create`) and receive a legitimately Shopify-signed body+HMAC (signed with the app's single shared `api_secret_key`).
2. Attacker captures the raw POST: `raw_body` and `x-shopify-hmac-sha256` header from that legitimate webhook delivery.
3. Attacker replays the exact same `raw_body` and `hmac` header directly to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the secret — see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`.
5. `Registry.process` invokes the host handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's own order data>, ...)` — see `lib/shopify_api/webhooks/registry.rb:188-200` — causing the app to process attacker-supplied content as if it belonged to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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
```
