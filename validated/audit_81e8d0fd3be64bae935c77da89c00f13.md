Confirms the docs explicitly document `data.shop` as "The shop domain of the webhook" and instruct handlers to key work off it (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), while `Registry.process` only validates `Utils::HmacValidator.validate(request)` against `request.to_signable_string` which is just `@raw_body`. The `shop` value itself comes purely from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, never included in the signed bytes. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing shop-domain spoofing on a validly-signed webhook request - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying that `Utils::HmacValidator.validate(request)` succeeds against `request.to_signable_string`, which returns only the raw request body. The `shop` value that is handed to the application's webhook handler as the tenant identifier is read directly from the `shopify-shop-domain` (or `x-shopify-shop-domain`) HTTP header — a value that is never part of the HMAC-signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` only [2](#0-1) , and `Registry.process` gates the entire trust decision on that single check: `raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` [5](#0-4) . Meanwhile `request.shop` is read straight from the `shop-domain` header with no cryptographic binding to the body or HMAC: `T.cast(shopify_header("shop-domain"), String)` [1](#0-0) .

The equality this breaks: `shop authenticated by HMAC == shop delivered to the handler`. In fact, the gem never checks this equality at all — the HMAC only proves "this body byte-string was signed with the app's `client_secret` at some point," not "this body was sent for shop X." The library documents that handler implementations are expected to trust `data.shop` as the source of truth for the webhook's tenant: "`shop`, `String` - The shop domain of the webhook" and the sample handler does `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [4](#0-3) . `Registry.process` itself forwards the unauthenticated header value straight into the metadata passed to the handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) .

Because a single app-level `client_secret` is used to validate every shop's webhooks (there is no per-shop key), any actor who can obtain one valid `(raw_body, hmac)` pair — trivially, by installing the app on their own store and receiving a webhook for an event they trigger themselves (e.g. creating an order in their own free/dev shop) — can capture that exact `(body, hmac)` and replay it to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. The HMAC check still passes because it only verifies the (unmodified) body against the secret; it says nothing about which shop the header claims. The application-level handler, following this gem's own documented usage pattern, will then process/attribute that (attacker-authored) body to the victim shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged actor who is merely a legitimate (even free-tier) merchant of the app can forge webhook deliveries that the app attributes to a different, victim merchant's shop, using data they fully control (their own order/product/etc. payload). Depending on the handler logic that host apps build against this documented API (e.g., updating shop-scoped records, provisioning, billing side effects, or triggering per-shop workflows), this enables cross-tenant data corruption or spoofed events for a store the attacker does not control — matching the "cross-tenant access" impact category, since the gem's own identity-binding primitive silently permits it.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (the common SaaS case): the attacker only needs to be a legitimate merchant of their own instance of the app (an unprivileged action, no special access token or leaked secret required) to obtain one valid signed body/HMAC pair, then can freely relabel it with any `shop-domain` header value when replaying it to the app's public webhook URL, since the gem performs no correlation between the header and the signed bytes.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or independently verify `request.shop` against an expected/known value (e.g., cross-check against a session previously established via OAuth/token-exchange for that shop, or require the shop header content to be embedded in and verified as part of the signed payload) before trusting it as the tenant identifier passed to `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own Shopify store (`attacker-shop.myshopify.com`) — a normal, unprivileged action.
2. Attacker triggers a webhook (e.g. `orders/create`) for their own store and captures the raw HTTP request Shopify sends to the app's webhook endpoint, including the `x-shopify-hmac-sha256` header and raw body.
3. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but changes the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4) , which only recomputes the HMAC over `@raw_body` [7](#0-6)  — unchanged from step 2 — so validation succeeds.
5. The handler is invoked with `WebhookMetadata` whose `shop` is `"victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store, letting the attacker inject/attribute data to the victim tenant.

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

**File:** docs/usage/webhooks.md (L10-26)
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
