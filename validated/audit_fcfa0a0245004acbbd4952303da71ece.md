### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the identity field `shop` from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but `Registry.process` only verifies the HMAC over the raw request body, never over that header. This breaks the binding: `shop asserted by header == shop the HMAC actually authenticates`. An attacker who can produce one valid `(raw_body, hmac)` pair for a shop they control (e.g., their own installed dev/test store) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the check in `Registry.process` will still pass.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from a header supplied by the HTTP caller, with no cryptographic binding to that value: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `raw_body`) and then hands `request.shop` straight to the app's handler as trusted identity: [3](#0-2) 

`HmacValidator.validate` computes/compares the HMAC purely from `verifiable_query.to_signable_string`, i.e. the body only: [4](#0-3) 

The `shop` field ends up in `WebhookMetadata`, which is documented as an identifier apps should use to route/attribute the event to a specific merchant/tenant (e.g., `data.shop` used to look up a session or enqueue tenant-scoped work), yet it was never part of what the HMAC signed: [5](#0-4) [6](#0-5) 

**Broken identity binding (equality that should hold but doesn't):**
`shop_authenticated_by_hmac == shop_header_value_used_by_handler`

Before the attacker's request: for a genuine Shopify webhook, both sides are equal because Shopify computes the HMAC and sets the header for the same shop event.

After the attacker's replay: the attacker keeps the original signed `raw_body` (so the HMAC check in `HmacValidator.validate` still succeeds), but swaps `x-shopify-shop-domain` to a victim shop's domain. `Registry.process` has no way to detect this because the header was never part of `to_signable_string`, so the equality silently fails while validation still reports success.

To obtain a valid `(raw_body, hmac)` pair, the attacker only needs to control one shop that has this app installed (e.g., a free Shopify partner/dev store), which is available to any unprivileged internet user — no access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Impact Explanation
This is a cross-tenant confusion: the app processes attacker-supplied data while believing it originates from an arbitrary shop of the attacker's choosing. If the host application uses `data.shop` from `WebhookMetadata` to select the merchant/session context, look up an access token, enqueue a job scoped to a shop, or write into per-tenant storage (which is exactly the pattern the gem's own webhook doc example demonstrates: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), the attacker can inject data attributed to a victim shop of their choosing, causing cross-tenant data poisoning under the guise of an "HMAC-verified" webhook. This matches the Critical class of cross-tenant access.

### Likelihood Explanation
Any internet user can create a free Shopify development store, install any app that uses this gem's webhook flow, and trigger a real webhook (e.g. `orders/create`) to capture a valid `(raw_body, hmac)` pair signed with the app's real secret. Replaying that captured body with an altered `shop-domain` header to the public webhook endpoint requires no further secrets. The only constraint is that the replayed body's contents (which reference the attacker's own resources) must be plausible to whatever the handler does with `data.body`/`data.shop`, but the shop identity itself is fully attacker-controlled once a single valid signature is obtained. `HmacValidator.validate` gives no indication that only the body — and not the shop — was authenticated.

### Recommendation
Include the shop domain (and other Shopify-set identity headers, e.g. `webhook-id`, `topic`) in the signable string used for HMAC verification, or otherwise cryptographically bind the header to the verified payload before it is exposed to the handler as `WebhookMetadata#shop`. At minimum, update `Request#to_signable_string` to incorporate the shop header, and document clearly that the current `shop` header is unauthenticated so host apps do not treat it as a trusted tenant identifier without independent verification (e.g., cross-checking against the shop's own stored `myshopify_domain`).

### Proof of Concept
1. Attacker installs the target app on their own dev store `attacker-shop.myshopify.com` and triggers a real webhook event (e.g. updates an order), capturing the resulting HTTP request: `raw_body = B`, `x-shopify-hmac-sha256 = H` (computed by Shopify over `B` with the app's real `api_secret_key`), `x-shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker sends a new POST to the app's webhook endpoint with the identical `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain = victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `B` and compares to `H` — this succeeds because `B` is unchanged. [7](#0-6) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, i.e. the app processes attacker-controlled body `B` as if it were an authenticated event for `victim-shop.myshopify.com`, even though the HMAC never covered the shop identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L10-27)
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
```
