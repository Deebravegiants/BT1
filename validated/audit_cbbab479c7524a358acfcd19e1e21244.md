This confirms the finding: `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which validates the HMAC over `request.to_signable_string`, and `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, and `webhook_id` fields are read straight from unauthenticated HTTP headers and are never included in the HMAC-signed content [2](#0-1) . The gem's own documentation instructs the handler to trust `data.shop` as the tenant identifier for dispatching work [3](#0-2) , and `Registry.process` passes that unverified header value directly into the `WebhookMetadata` struct delivered to the handler [4](#0-3) .

### Title
Webhook shop/topic/webhook-id headers are trusted for tenant identification without being covered by the HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw JSON body. The `shop-domain`, `topic`, and `webhook-id` values that the handler uses to identify which merchant/tenant and event the payload belongs to are taken from HTTP headers that are completely outside the HMAC's coverage, so they can be freely set by anyone who can reach the endpoint with a body/HMAC pair.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field [5](#0-4) . For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body` [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors read directly from the (attacker-suppliable) headers `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` [2](#0-1) , none of which participate in the signature computation.

`Registry.process` only checks `Utils::HmacValidator.validate(request)` — i.e., "is this body byte-for-byte something that was HMAC'd with our secret at some point" — and then unconditionally builds `WebhookMetadata` from the unverified headers and dispatches to the app's handler [4](#0-3) .

The broken identity binding, expressed as an equality that the code fails to enforce:
`hmac_verified(raw_body)` ≠ `authenticated(shop_header, topic_header, webhook_id_header)`

Concretely: if any party (e.g., an attacker's own trial/dev store) obtains one genuine Shopify webhook delivery (raw body + valid `x-shopify-hmac-sha256` computed by Shopify with the app's `client_secret`) for topic X, they can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting `x-shopify-shop-domain` with a victim shop's domain, `x-shopify-topic` with a different registered topic that expects a compatible body shape, and any `x-shopify-webhook-id`. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will look up the handler for the attacker-chosen topic and hand it `WebhookMetadata` claiming the victim's shop domain [6](#0-5) . Any host application that follows the gem's own documented pattern — dispatching background work keyed off `data.shop` — is misled into associating attacker-controlled content with a shop it did not originate from [7](#0-6) .

### Impact Explanation
This breaks the tenant identity binding at the point the library hands data to the app: `WebhookMetadata#shop` is supposed to be the authenticated, Shopify-attested origin of the event, but it is not authenticated by the gem at all — it's a bare header. Any application logic built purely on this library's contract (verify → get authenticated shop) is exposed to cross-tenant data confusion: work can be enqueued, cache entries updated, or shop-scoped state mutated as if it came from shop A while data actually originated in shop B's webhook, since the body's HMAC only ever proves it was signed for *some* shop, not the one in the header.

### Likelihood Explanation
This requires an attacker to already receive at least one legitimate webhook of a given topic (e.g., by installing the app on their own store, which is normally something any developer can do for a public/whitelisted app) and then to replay that body directly to the app's public webhook URL with modified headers. Reaching the target endpoint requires no credentials beyond knowing its URL, which is typically public/predictable (documented registration `path`). No access to `api_secret_key` or any merchant's access token is needed.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable content for `Webhooks::Request`, or otherwise cryptographically bind them to the payload before use, rather than relying solely on the body's signature. At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated and that host applications must independently cross-check `data.shop` against a known/installed-shop list before trusting it for tenant-scoped operations.

### Proof of Concept
1. Register two topics in the app, e.g. `orders/create` and `orders/updated`, with a handler that dispatches `perform_later(shop_domain: data.shop, webhook: data.body)`.
2. As an attacker, install the target app on your own store (`attacker.myshopify.com`) and capture one legitimate `orders/create` webhook: raw body `B` with header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's secret).
3. POST the same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` and `x-shopify-topic: orders/create`.
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (it only checks `B` against `H`), `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "orders/create", body: parsed(B), ...)`, and the handler processes attacker-supplied content as if it were authentic data from `victim.myshopify.com` [6](#0-5) .

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
