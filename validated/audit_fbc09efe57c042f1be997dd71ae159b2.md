### Title
Webhook shop/topic identity is trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so `Utils::HmacValidator.validate` binds the HMAC exclusively to `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never included in the signed data, yet `Registry.process` passes them straight through to the app's webhook handler as the authoritative shop/topic identity.

### Finding Description
`Utils::VerifiableQuery`/`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the object [1](#0-0) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from the (attacker-reachable) HTTP headers of the request and are not part of what is hashed [2](#0-1) .

`Registry.process` validates the HMAC over the body only, and then constructs `WebhookMetadata` using `request.shop` and `request.topic` taken straight from those unauthenticated headers, handing them to the registered handler as trusted identity fields: [3](#0-2) 

This breaks the intended binding: `HMAC-verified(body) == HMAC-verified(body, shop, topic)`. In reality the equality only holds for the left side; `shop`/`topic`/`webhook_id` are asserted, not authenticated. Any caller who can obtain one valid `(raw_body, hmac)` pair (e.g., by triggering a webhook delivery to a shop they control, which is trivial since anyone can install/operate a Shopify development store and register webhooks against this same app) can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` / `shopify-topic` header. The gem will report a successful HMAC validation and dispatch the handler believing the event belongs to a different shop/topic than the one that actually produced the signed body.

### Impact Explanation
Applications built on this gem are documented to key their handler logic off `data.shop` (e.g. looking up the shop's session/access token, updating shop-scoped records) exactly as shown in the gem's own webhook docs [4](#0-3) . Since `shop` is not cryptographically bound to the payload, an attacker can make the app process a validly-signed body under a victim shop's identity (or vice versa), leading to cross-tenant data association/confusion in the host application's webhook handling — a violation of the tenant boundary this gem is supposed to enforce via HMAC verification.

### Likelihood Explanation
The attacker only needs to be able to generate one legitimate webhook (any shop they control, and any topic they can subscribe an app instance to) to obtain a valid `(body, hmac)` pair, then send an unauthenticated HTTP POST to the app's public webhook endpoint with forged `shopify-shop-domain`/`shopify-topic`/`shopify-webhook-id` headers. No secrets, tokens, or privileged access are required — this is reachable by any unprivileged internet user who knows/guesses the app's webhook endpoint.

### Recommendation
Include the identity-bearing fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material, or otherwise cryptographically bind them to the payload before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, `to_signable_string` for `Webhooks::Request` should incorporate these header values (e.g., via a canonicalized concatenation with the body) so `Utils::HmacValidator.validate` fails if any of them are altered.

### Proof of Concept
1. Attacker owns/controls `attacker-shop.myshopify.com` and registers the app's webhook for topic `orders/create`.
2. Shopify delivers a legitimately-signed webhook to the app: `raw_body = B`, header `shopify-hmac-sha256 = H = HMAC(secret, B)`, `shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` and replays a new POST to the same app endpoint, keeping `raw_body = B` and `shopify-hmac-sha256 = H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes `HMAC(secret, B)`, which still equals `H`, so validation succeeds.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches the handler, which now processes attacker-controlled body content under the victim shop's identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
