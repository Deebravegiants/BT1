### Title
Webhook shop/topic identity headers are not covered by the HMAC, allowing cross‑tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the tenant‑identifying fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) come from HTTP headers that are never part of the signed content. `ShopifyAPI::Utils::HmacValidator.validate` only proves that *some* body was signed with the app's shared `api_secret_key`; it proves nothing about which shop, topic, or webhook id that signature belongs to.

### Finding Description
`Registry.process` performs exactly one check before dispatching to the app's handler: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string`: [2](#0-1) 

and `Request#to_signable_string` is defined as just the raw body: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker‑controllable HTTP headers with no cryptographic binding to the body or to each other: [4](#0-3) 

These unauthenticated values are then handed directly to the app's handler as the tenant identity for the event: [5](#0-4) 

The library's own documentation instructs integrators to key downstream per‑tenant work off `data.shop` exactly as delivered: [6](#0-5) 

Because `api_secret_key` is shared across every shop that has installed the app (it is not per‑shop), any body+HMAC pair that was ever legitimately produced for one installation remains a cryptographically valid pair for the same body content. Nothing in `Request`/`HmacValidator`/`Registry` binds that valid signature to the specific `shop-domain` header it was originally delivered with — an attacker who can present that same raw body and HMAC to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` value will pass validation and cause the app to process the event as if it came from an arbitrary victim shop.

This directly matches the "field acted on but not covered by the HMAC" identity‑binding break called out in the task: the equality the code implicitly assumes is `hmac_valid(body) == hmac_valid_for(shop, topic, webhook_id, body)`, but the actual check only proves `hmac_valid(body)`.

### Impact Explanation
If an attacker obtains one valid `(raw_body, hmac)` pair (e.g., from their own shop's webhook delivery, from logs, from a proxy/tunnel used during development, or any other legitimate delivery to the shared endpoint), they can replay it while claiming an arbitrary `shop-domain`. Any host application that trusts `WebhookMetadata#shop` — exactly as this gem's own documentation recommends — to route data or trigger per‑tenant side effects (e.g., enqueue `perform_later(shop_domain: data.shop, ...)`, update shop‑scoped records, trigger mandatory GDPR redaction flows) will act on behalf of the wrong tenant. This is a cross‑tenant identity confusion condition.

### Likelihood Explanation
Exploitability depends on the attacker first acquiring a legitimate `(body, hmac)` pair for the shared `api_secret_key`; this is plausible for at least one shop the attacker controls (their own installation, or via development tooling positioned in front of their own webhook endpoint), but does not require compromising the app's secret itself or MITM'ing Shopify's delivery to the victim shop. Given that a single captured pair is reusable against any tenant of the same app, likelihood is moderate rather than trivial to fully verify without a live deployment, but the root cause — no identity header is covered by the signature — is concretely demonstrated in the code cited above.

### Recommendation
Include the identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC‑signable content, or independently verify `request.shop` against the known set of shops that have valid sessions/installations for the app before dispatching to a handler, so a signature valid for one shop cannot be replayed as valid for another.

### Proof of Concept
1. App has two installs, Shop A (attacker) and Shop B (victim), both under the same `api_secret_key`.
2. Attacker triggers/receives a legitimate webhook for Shop A, capturing `raw_body` and its `X-Shopify-Hmac-Sha256` value (e.g., via a request-inspection proxy in front of their own endpoint, which is standard developer tooling, not TLS interception of Shopify's channel).
3. Attacker POSTs the same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook route, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only hashes `raw_body`; `Registry.process` dispatches `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` to the handler, which the app treats as an authentic event for Shop B. [1](#0-0) [7](#0-6)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L1-38)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
