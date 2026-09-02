This confirms the root cause: `ShopifyAPI::Utils::HmacValidator.validate` only verifies `request.to_signable_string`, which for `ShopifyAPI::Webhooks::Request` is `@raw_body` alone [1](#0-0) . The `shop` field, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signable string and thus never covered by the HMAC [2](#0-1) . `Registry.process` validates only the HMAC of the body and then forwards `request.shop` unchanged into `WebhookMetadata`, which is what the host app's handler treats as the tenant identifier [3](#0-2) . The documented handler contract explicitly tells integrators to trust `data.shop` as "The shop domain of the webhook" and to use it to key their per-tenant business logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [4](#0-3) .

### Title
Webhook shop-domain header is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, while `shop` (and `topic`, `webhook_id`, `api_version`) are taken straight from unauthenticated HTTP headers. `HmacValidator.validate` verifies the HMAC solely against the body, so the `shop` value that `Registry.process` hands to app-provided webhook handlers is never bound to the signature that "authenticates" the request.

### Finding Description
The equality that should hold is: `hmac == HMAC(api_secret_key, shop || body)` (i.e., the tenant identifier must be cryptographically bound to the signature). Instead the gem computes `hmac == HMAC(api_secret_key, body)` only [5](#0-4) , and separately reads `shop` from a header that isn't part of that computation [2](#0-1) .

Before the attacker's request: a legitimate webhook for shop A arrives as `POST /webhook` with header `X-Shopify-Shop-Domain: shop-a.myshopify.com`, body `B`, and `hmac = HMAC_secret(B)`.

After the attacker's request: the attacker (any internet user who can reach the app's public webhook endpoint, and who can obtain one valid `(body, hmac)` pair — trivially available since they can install the app on their own free/dev store, or since `body` for many topics like `app/uninstalled`, `shop/redact`, etc. is predictable/replayable) replays the exact same `body`/`hmac` pair but substitutes `X-Shopify-Shop-Domain: shop-b.myshopify.com`. `HmacValidator.validate` still returns `true` because it only checked `body` against `hmac` [6](#0-5) . `Registry.process` then builds `WebhookMetadata` with `shop: request.shop` set to the attacker-chosen value and invokes the app's handler as if the event genuinely originated from shop B [7](#0-6) .

### Impact Explanation
Because the gem's own documentation instructs integrators to key tenant-scoped side effects (persistence, job enqueue, `app/uninstalled` cleanup, GDPR `shop/redact`/`customers/redact` handling, etc.) directly off `data.shop` [8](#0-7) , an attacker who can produce or capture any one valid `(body, hmac)` pair for the shared `api_secret_key` can forge webhook events attributed to any other shop, causing the app to process fabricated events cross-tenant. This matches the Critical "cross-tenant access" impact category, since the tenant-scoping field is not part of the authenticated payload.

### Likelihood Explanation
The webhook endpoint is by design a public, unauthenticated HTTP endpoint (no TLS client cert, no bearer token). The only gate is `HmacValidator.validate`, and it never binds `shop`. Any actor able to install the app on even a free/dev store receives real, validly-signed webhook bodies for arbitrary topics against the app's shared `api_secret_key`, and can then freely replay those bodies with a different `shop-domain` header value to the app's endpoint. No privileged credentials, access tokens, or `client_secret` disclosure are required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` value to the verified payload before it is passed to `WebhookMetadata`/handlers — e.g., have `VerifiableQuery#to_signable_string` for `Webhooks::Request` incorporate `shop_domain` alongside `@raw_body`, matching how `Oauth::AuthQuery#to_signable_string` binds all relevant fields [9](#0-8) . Short of a body-embedded scheme, the library should also document/enforce that hosts cross-check `request.shop` against the shop that registered the specific `webhook_id`/subscription.

### Proof of Concept
1. Attacker installs the target app on their own store, triggering a legitimate webhook delivery with body `B` and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, signed as `hmac = HMAC(api_secret_key, B)`.
2. Attacker replays `POST <app_webhook_path>` with the same body `B` and same `hmac`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and succeeds [6](#0-5) .
4. The registered handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` [7](#0-6) , causing the host application to process a forged, cross-tenant webhook event as genuine.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
