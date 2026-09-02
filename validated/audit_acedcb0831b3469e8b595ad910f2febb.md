### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted for tenant dispatch despite not being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw body against the HMAC, but then dispatches to the handler using the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers. This breaks the identity binding `authenticated_bytes == acted_upon_bytes`, exactly the bug class described in the report (a field acted on but not covered by the cryptographic guarantee).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers and are not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., only the body), then immediately trusts `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (the raw body only) using `Context.api_secret_key`: [4](#0-3) 

The identity binding that should hold is: `signed_bytes == (body, shop, topic)`. In reality: `signed_bytes == body` while `acted_upon_identity == (shop_header, topic_header)`. Because the HMAC never covers the `shop-domain` header, any pairing of a valid `(body, hmac)` pair with an arbitrary `shop-domain`/`topic` header value passes validation and is delivered to the handler as if it came from that shop/topic. The gem's own documentation instructs app authors to key their per-tenant processing directly off `data.shop`: [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity-binding break: the same signed payload (captured once, e.g. via logs, a proxy, error monitoring tooling, or any other channel where the raw body + HMAC header become visible) can be replayed against the app's public webhook endpoint with a different `shopify-shop-domain` header, and the `HmacValidator` will still validate because it only checks the body against the secret it shares with Shopify — it has no way to tell which shop the body was meant for. Since `Registry.process` hands `request.shop` straight to the handler, and the gem's documented usage pattern is for host apps to use `data.shop` to select which merchant's data/session to update, this allows cross-tenant data confusion/write against a store the attacker does not actually control the webhook for, satisfying the "cross-tenant access" criterion for Critical impact. The topic field is equally unauthenticated, so a captured payload for one topic could also be misrouted to a different handler by relabeling `shopify-topic`.

### Likelihood Explanation
Exploitability requires the attacker to obtain one legitimate `(raw_body, hmac)` pair for any shop using the app (not necessarily the victim shop) — e.g., through log exposure, browser/network capture in a shared environment, or replaying their own app's webhook to a different registered shop record if the app doesn't otherwise partition by an authenticated tenant identifier. This does not require the `api_secret_key`, an access token, or any privileged credential; it only requires network access to the app's public webhook endpoint and one previously observed valid webhook delivery. This is a design property shared with Shopify's actual webhook signing scheme (only the body is signed), but the gem provides no additional binding or warning, and downstream apps following the documented `data.shop`-based pattern are directly exposed.

### Recommendation
- Do not treat header-derived `shop`, `topic`, `webhook_id` as authenticated. At minimum, cross-check the `shop` header against the shop associated with the webhook subscription (e.g., by validating it belongs to a shop the app has an active session/installation for) before acting on it.
- Where feasible, bind the `shop` and `topic` into the value verified by `HmacValidator` (e.g., include them in the signable string alongside the body) rather than relying solely on `@raw_body`.
- Document explicitly in `docs/usage/webhooks.md` that `data.shop`/`data.topic` are unauthenticated header values and that host apps must independently verify shop identity (e.g., against known installed shops) before performing tenant-scoped writes.

### Proof of Concept
1. App has webhook handler `WebhookHandler` registered for topic `orders/create`, dispatching `perform_later(shop_domain: data.shop, webhook: data.body)` as shown in the gem's own docs.
2. Attacker captures one legitimate webhook delivery for Shop A: raw body `B` and header `x-shopify-hmac-sha256: H` (H = HMAC-SHA256(secret, B)), obtained via a log leak, proxy, or any means not requiring the app's secret.
3. Attacker POSTs the same raw body `B` and header `x-shopify-hmac-sha256: H` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a different shop) and/or a different `x-shopify-topic`.
4. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` against the shared secret — it never inspects the `shop-domain` header. [6](#0-5) 
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the attacker-controlled headers and calls `handler.handle`, causing the app to process Shop A's payload as if it belongs to `shop-b.myshopify.com`. [7](#0-6)

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
