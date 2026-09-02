### Title
Webhook `shop` domain is trusted from an unauthenticated header while the HMAC only covers the raw body, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` domain that the framework hands to the app's handler is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `#shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that same signature: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (i.e., the body) and the shared `api_secret_key`: [4](#0-3) 

This breaks the identity binding: `shop-domain header value == shop that produced/owns the signed body` is never checked. The `api_secret_key` (client_secret) used to sign webhooks is the same for every shop that installs a given app - it is not shop-specific. Consequently, any of the app's own merchants (an "unprivileged" party with respect to *other* tenants, but a legitimate holder of validly-signed webhook payloads for their own shop) can capture a genuine webhook body Shopify sent for their shop, and replay that exact raw body to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g. a victim shop). Because the HMAC check only verifies the bytes of the body against the shared secret, it will still pass, and `Registry.process` will dispatch the handler with `data.shop` set to the attacker-chosen victim domain, per the documented handler contract (`data.shop` is described as "The shop domain of the webhook"): [5](#0-4) 

Downstream app code (as shown in the gem's own documented usage example) uses `data.shop` to key business logic/storage per tenant: [6](#0-5) 

### Impact Explanation
Because the gem exposes `data.shop` as an authenticated-looking identity field without actually verifying it against the signed payload, any host application that follows this gem's own documented pattern (using `data.shop` to select the tenant/session context) is vulnerable to cross-tenant data injection/confusion: an attacker who legitimately installed the app on their own store can forge webhook events "from" another merchant's shop. This matches the Critical category "cross-tenant access," since it lets one tenant's data (or attacker-crafted body reusing another topic) be attributed to and processed under a different tenant's identity within the app relying on this gem.

### Likelihood Explanation
Likelihood is high for any app that installs itself on multiple shops with a single client/app secret (the standard Shopify app model) and follows this gem's documented pattern of trusting `data.shop`. The attacker only needs to run the app on their own store to obtain a body with a valid HMAC, then replay it to the public webhook endpoint with a modified shop header - no access to `client_secret`, tokens, or victim credentials is required.

### Recommendation
Include the shop domain (and ideally other identity-relevant headers such as `webhook_id`/topic) in the signed payload used for HMAC verification, or otherwise cryptographically bind the `shop-domain` header to the request before trusting it, e.g., verify `request.shop` against the shop associated with the specific `webhook_id`/subscription server-side, rather than accepting an unauthenticated header value as the tenant identity handed to `WebhookMetadata`.

### Proof of Concept
1. App `X` is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, sharing the same `api_secret_key`.
2. Shopify sends a legitimate webhook to app `X` for `attacker-shop.myshopify.com`:
   - Headers: `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC of raw body>`
   - Body: `{"id": 123, ...}`
3. Attacker captures this raw body and its valid HMAC (trivial since it's their own shop/webhook).
4. Attacker POSTs the same raw body and HMAC to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which only hashes `@raw_body` - the swapped header does not affect the check, so validation succeeds.
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes/stores the attacker-controlled body under the victim's tenant context, per the gem's documented handler pattern.

### Citations

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L19-29)
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
