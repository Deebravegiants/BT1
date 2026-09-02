This confirms the vulnerability. The gem's own documentation explicitly instructs developers to treat `data.shop` (sourced from the `x-shopify-shop-domain` header) as the trusted tenant identifier, while the HMAC only covers the raw body.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely by checking `Utils::HmacValidator.validate(request)` against the raw request body, then trusts the unauthenticated `shop-domain` header to build the `WebhookMetadata` passed to the app's handler. Because the HMAC signature never covers the shop-domain header, an attacker who possesses one authentically-signed webhook body (e.g., from installing the app on their own store) can replay that same body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. The signature still validates, and the host application's handler receives `data.shop` set to the attacker-chosen (potentially victim) shop domain.

### Finding Description
`ShopifyAPI::Webhooks::Request` includes `Utils::VerifiableQuery` and defines: [1](#0-0) 
`to_signable_string` returns only `@raw_body` — none of the headers, including `shop-domain`, are part of the signed material. `shop` is read directly from an unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then constructs `WebhookMetadata` using `request.shop` (the unauthenticated header) and dispatches it to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the signature purely from `to_signable_string`, i.e., the raw body — the shop identity is never part of the equality check: [4](#0-3) 

This breaks the intended binding `authenticated_shop == shop_used_by_handler`. The gem's own documentation instructs developers to treat `data.shop` as the trusted per-tenant identity to route/act on: [5](#0-4) [6](#0-5) 

### Impact Explanation
Since a webhook is HMAC-valid as long as the body content matches the signature (which any shop that has the app installed can legitimately obtain by triggering an event on their own store), an attacker in control of one shop can forge the `shop-domain` header to any arbitrary value and have the app process the payload as if it originated from a different (victim) shop. Any host application that relies on the library's exposed `data.shop` to select per-tenant state, enqueue per-tenant jobs, or write to per-tenant records (as explicitly recommended in the gem's own documentation and breaking-changes guide) can be tricked into cross-tenant data corruption or disclosure — an unprivileged internet user with access to only their own shop's webhook traffic can inject/spoof events attributed to another merchant's shop.

### Likelihood Explanation
Likelihood is high: no privileged credentials beyond installing the app on any (even the attacker's own) shop are required, and this identity-binding gap is inherent to the library's shipped `Request`/`Registry.process`/`WebhookMetadata` design, not misuse by the host app. The attack requires no knowledge of the `api_secret_key` — only a previously observed valid `(body, hmac)` pair for any topic the attacker's own shop can trigger, plus the ability to send an HTTP POST to the app's public webhook endpoint with a modified header.

### Recommendation
Bind the shop identity into the verified payload before trusting it downstream. Recommended remediation: extend `VerifiableQuery`/`to_signable_string` (or add a separate verification step in `Registry.process`) so the `shop-domain` (and ideally `topic`, `webhook_id`) headers are included in the data covered by the HMAC comparison, or alternatively, cross-check the header-derived shop against a shop known to have installed the app for that specific `webhook_id`/subscription before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers `orders/create`, capturing the legitimate webhook `raw_body` and its `x-shopify-hmac-sha256` value (both are attacker-observable since it's their own shop's webhook traffic hitting their own app-controlled endpoint, or via any other route that surfaces this pair).
2. Attacker POSTs to the app's public webhook route with the *same* `raw_body`/`x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `raw_body` — it matches, since the body/signature pair is unmodified.
4. `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` using the spoofed `victim-shop.myshopify.com`, and the app handler executes tenant-scoped logic (e.g., `perform_later(shop_domain: data.shop, ...)`) against the victim shop's tenant context, as shown in the gem's documented usage pattern.

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
