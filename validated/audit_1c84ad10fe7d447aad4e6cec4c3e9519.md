## Title
Webhook shop-domain (and topic) spoofing due to HMAC covering only the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` in `ShopifyAPI::Webhooks::Registry.process` cryptographically authenticates the *body* only. The `shop`, `topic`, `webhook_id`, and `api_version` values — all read straight from unauthenticated HTTP headers — are never bound to that signature, yet they are forwarded as authenticated fields (`WebhookMetadata`) to the app's handler and are documented as verified data "that did indeed come from Shopify."

### Finding Description
`lib/shopify_api/webhooks/request.rb` defines: [1](#0-0) 
`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers (`shopify_header`), while `to_signable_string` — the only input to the HMAC check — is just `@raw_body`.

`Registry.process` validates the HMAC and then unconditionally trusts these header-derived fields: [2](#0-1) 

The gem's own documentation instructs app authors to treat `data.shop` as a verified attribute of an authenticated Shopify request and to key application/tenant logic (e.g. job dispatch) off it directly: [3](#0-2)  — "This will verify the request did indeed come from Shopify," followed by an example that does `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`.

Because the HMAC is computed over `client_secret` (the app's single shared secret across all shops that installed the app) and the raw body only, the equality that should hold — `shop header used by the handler == shop that the signed body was actually produced for` — is not enforced anywhere. Any party who can obtain one legitimately-signed `(raw_body, hmac)` pair for their own shop (trivial: install the public app on their own store and capture the webhook their own server receives) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting a different `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) header. `HmacValidator.validate` recomputes the HMAC purely from `@raw_body`, so it still succeeds, and `Registry.process` calls the handler with `WebhookMetadata` claiming the payload belongs to an arbitrary victim shop/topic of the attacker's choosing.

### Impact Explanation
This breaks the tenant binding between "shop whose secret produced this signed payload" and "shop the app processes this data for," letting an attacker cause the app to attribute their own shop's webhook content (order data, product data, GDPR payloads, etc.) to a different, victim shop, or to relabel it under a different topic (e.g., turning a low-sensitivity `products/update` into a `customers/redact` handler invocation) — a cross-tenant data/authorization confusion inside the host app that this gem is supposed to prevent via `Registry.process`'s advertised authenticity guarantee.

### Likelihood Explanation
Any unprivileged internet user can self-install a public Shopify app to obtain a legitimately signed webhook to their own endpoint, then replay it with modified metadata headers to the app's same publicly reachable webhook URL — no access token, `client_secret`, or privileged account is required.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC validation, or otherwise cryptographically bind them to the body before trusting them in `WebhookMetadata`, so `Registry.process`'s claim of verifying "the request did indeed come from Shopify" actually covers the fields the handler relies on.

### Proof of Concept
1. Attacker installs the target public app on their own dev shop `attacker.myshopify.com`; app registers `orders/create` webhook to `POST /callback/orders/create`.
2. Shopify sends a webhook to attacker's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, body `B`.
3. Attacker resends the exact same request to the app's webhook endpoint, unchanged body `B` and `hmac`, but with `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `Digest.hexencode(...)` against `@raw_body` [4](#0-3) .
5. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's order JSON>, ...)`, and the host app processes attacker-controlled order data as if it belonged to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
