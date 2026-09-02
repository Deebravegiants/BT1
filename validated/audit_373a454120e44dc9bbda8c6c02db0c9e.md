This confirms the finding. The `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read from the unauthenticated `shopify-shop-domain` header [2](#0-1) . `Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)` and then hands `request.shop` straight to the handler as the tenant identifier [3](#0-2) . The documented handler contract explicitly treats `data.shop` as the shop domain of the webhook to be used for tenant-scoped work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [4](#0-3) .

### Title
Webhook tenant (`shop`) attribution is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the webhook HMAC only over the raw request body. The `shop` (tenant) attribute, however, is taken from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed payload. `Registry.process` accepts any request whose body-HMAC is valid and then forwards the caller-supplied `shop` header value, unchecked, to the app's webhook handler as the authoritative tenant identifier.

### Finding Description
The identity binding that should hold is:
`shop authenticated by HMAC == shop attributed to the processed webhook data`

- The HMAC is computed and verified purely against `@raw_body`: [1](#0-0) 
- `shop` is read directly from request headers, independent of the signed body: [2](#0-1) 
- `Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e., the body) against the HMAC secret: [5](#0-4) 
- `Registry.process` performs this HMAC check, then immediately trusts `request.shop` (header value) to construct `WebhookMetadata` passed to the handler: [3](#0-2) 

Because the same `api_secret_key` is used for the app's HMAC across all installed shops, any body+HMAC pair that is valid for shop A's webhook is *also* valid for a forged request claiming to be from shop B, since the header carrying the shop identity is never part of the signed material. An unprivileged merchant who has installed the app (and therefore legitimately receives real, correctly-signed webhooks for their own shop) can capture one such body/HMAC pair and replay it to the app's public webhook endpoint with the `shopify-shop-domain` header rewritten to point at a victim shop. `Registry.process` will accept it (the HMAC over the body still validates) and pass the forged `shop` value straight to the host app's handler as if it were an authentic webhook for the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an attacker-controlled body can be attributed to an arbitrary victim shop, since `shop` is never bound to the same signature that authenticates the payload. Per the documented handler contract, host applications are expected to key persistence/business-logic (e.g., which shop's order/product record to update) directly off `data.shop` [4](#0-3) , so this enables cross-tenant data injection into another merchant's account within the app, using only credentials the attacker already legitimately possesses (their own installed shop's webhook traffic).

### Likelihood Explanation
Exploitation requires only that the attacker be an installed/unprivileged merchant of the app who can observe at least one legitimately-signed webhook body/HMAC pair sent to their own webhook endpoint (trivial, since these are delivered to the app's own public HTTP route) and can then send a raw HTTP request to that same public endpoint with a modified `shop` header. No access to `api_secret_key`, access tokens, or victim credentials is required.

### Recommendation
Include the shop domain (and ideally webhook id/topic) inside the HMAC-signed material, or otherwise cryptographically bind the `shop` header value to the verified payload before it is handed to the handler — e.g., verify that `request.shop` matches a shop for which the app holds an active, previously-issued session/webhook registration record, rather than trusting the header value outright.

### Proof of Concept
1. App has two installed shops: `attacker.myshopify.com` and `victim.myshopify.com`.
2. Shopify sends a legitimate webhook to the app for `attacker.myshopify.com`:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
   - Body: `{"id": 1, "note": "hello"}`
3. Attacker captures this body + HMAC and replays it to the app's webhook endpoint with the header changed to `x-shopify-shop-domain: victim.myshopify.com`, leaving body and HMAC untouched.
4. `Utils::HmacValidator.validate` (via `ShopifyAPI::Webhooks::Registry.process`) succeeds because it only checks the HMAC against the unchanged raw body [6](#0-5) .
5. `handler.handle` receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's body [7](#0-6) , causing the host app to process attacker-controlled data as if it belonged to the victim shop.

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

**File:** docs/usage/webhooks.md (L10-30)
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
