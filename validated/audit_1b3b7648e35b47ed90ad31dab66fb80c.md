### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by the HMAC signature, allowing a valid-signature webhook to be replayed with a forged shop identity - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read directly from attacker-controllable HTTP headers [2](#0-1) . `Registry.process` validates only the body's HMAC and then forwards the unauthenticated `shop` header straight to the app's webhook handler as the tenant identifier [3](#0-2) .

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body` [4](#0-3) [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors are derived purely from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`), which are never included in the signed material [2](#0-1) .

`Registry.process` validates the HMAC on the body, then uses `request.topic` to select a handler and passes `request.shop` unchanged into `WebhookMetadata`, which is delivered to the app's handler as the authoritative shop identity [3](#0-2) . The gem's own documentation instructs integrators to treat `data.shop` as "The shop domain of the webhook" and use it directly (e.g., to enqueue background jobs keyed by shop) [5](#0-4) .

This breaks the identity binding: **bytes verified (body only) ≠ shop identity trusted (header, unauthenticated)**. Any unprivileged internet user who can obtain one legitimate `(body, hmac)` pair — trivially available since they can install the app on their own store and capture their own webhook delivery — can replay that exact body+HMAC pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. The HMAC check still passes because the header is not part of the signed content, so the request is accepted as authentic, but the `shop` value the app receives is entirely attacker-chosen.

### Impact Explanation
This falls squarely in the "shop authenticated versus the shop stored as a session key" bug class named in the rules. A host application that follows the gem's documented pattern — trusting `data.shop` from a passed-HMAC-check webhook to key session lookup, attribute data, or perform per-tenant actions — can be made to associate attacker-supplied (or victim-shop) content/actions with the wrong tenant, or process a replayed payload under a false shop identity, causing cross-tenant data confusion. Because the library performs no cross-check between the authenticated bytes and the claimed shop, the vulnerability is directly reachable through this gem's own webhook-processing API (`Registry.process`) with no access token, `client_secret`, or privileged account required — the attacker only needs a valid webhook capture from their own store or a captured delivery.

### Likelihood Explanation
High likelihood for any unprivileged actor: obtaining a legitimate `(body, hmac)` pair requires nothing more than installing the target app on a store the attacker controls (a normal, unprivileged action), then replaying the raw POST body and HMAC header to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. No secret material, TLS interception, or social engineering is needed. The severity of the resulting impact depends on how the host application uses `data.shop`, but the gem's own documentation actively encourages using it as an unguarded tenant key.

### Recommendation
Extend `Webhooks::Request#to_signable_string` (or add a companion binding check in `Registry.process`) so that the `shop`, `topic`, and `webhook_id` header values are cryptographically bound to the signed payload, or, at minimum, document loudly that `data.shop` is unauthenticated and must not be used as a trust boundary without independently verifying that a webhook subscription/session exists for that shop and topic combination before acting on the payload.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, unprivileged) and triggers any subscribed webhook (e.g., `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker replays this exact `(raw_body, hmac)` pair to the app's webhook endpoint, but overwrites `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged shop header [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the (still valid) HMAC [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from and describes `attacker-shop.myshopify.com` [8](#0-7) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L12-27)
```markdown
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
