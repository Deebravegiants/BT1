This confirms the vulnerability: the gem-documented flow is entirely reliant on `data.shop` from `WebhookMetadata` for tenant identification, yet that value comes from an HMAC-unprotected header.

### Title
Webhook `shop` field is trusted for tenant identification but excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop` is read directly from the `X-Shopify-Shop-Domain` header without being part of the signed content [2](#0-1) . `Registry.process` validates the HMAC over that same signable string and, once it passes, hands `request.shop` straight to the app's handler as the tenant identifier, with no separate binding check [3](#0-2) .

### Finding Description
The equality that should hold is: `hmac == HMAC(secret, body ‖ shop)` such that the `shop` attributed to a webhook is cryptographically bound to the same signature that authenticates the body. Instead the gem computes and checks `hmac == HMAC(secret, body)` only [4](#0-3) , and separately reads `shop` from an unauthenticated header [2](#0-1) .

Before the attack: a legitimate webhook for shop A arrives with `body`, a valid `hmac` computed over `body`, and `shop-domain: shop-a.myshopify.com`. `HmacValidator.validate` succeeds because the signature matches `body`, and `Registry.process` passes `shop: request.shop` (`shop-a`) to the handler [3](#0-2) .

After the attacker's request sequence: an unprivileged internet user (who owns shop B and thus legitimately receives webhooks addressed to shop B, complete with a valid `hmac` over their own body) replays that exact `body`/`hmac` pair to the app's webhook endpoint but substitutes the `X-Shopify-Shop-Domain` header with shop A's domain (or any victim domain). `HmacValidator.validate` still succeeds, because it only checks `body` against `hmac` — the `shop` header was never part of the signed content — so `Registry.process` calls the handler with `shop: "shop-a.myshopify.com"` and shop B's data [3](#0-2) . The app, following the gem's documented pattern of using `data.shop` as the tenant key [5](#0-4) , will process/store attacker-supplied data under the victim tenant's identity — a direct cross-tenant write/identity confusion enabled purely by this gem's verification logic.

### Impact Explanation
This breaks the tenant boundary the gem is responsible for establishing: `HmacValidator` is the only authenticity check performed before webhook data is dispatched to the host app, and it silently omits the one field host apps are told to rely on for shop attribution. Any internet user who can trigger webhooks for a shop they control (trivial — install a free/dev app on any shop) can forge cross-tenant events against every application built on this gem's webhook API, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: the attacker doesn't need `api_secret_key`, an access token, or any privileged credential — only a shop of their own (or any single valid captured webhook payload/HMAC pair) and the ability to send an HTTP request with a modified header to the app's public webhook endpoint. No race condition, timing, or interception is required.

### Recommendation
Bind `shop` into the signed material verified by `HmacValidator`, e.g. by including the `shop-domain` header (and other identifying headers like `topic`/`webhook-id`) in `Webhooks::Request#to_signable_string`, or by independently authenticating the shop identity via a mechanism validated against the same secret before it is exposed through `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, headers including `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical `raw_body` (`B`) and identical `hmac` header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds a request whose `to_signable_string` is still `B` [1](#0-0) .
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and successfully matches the forged request's `hmac` [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [7](#0-6)  — the host app now processes attacker-controlled data as if it belonged to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
