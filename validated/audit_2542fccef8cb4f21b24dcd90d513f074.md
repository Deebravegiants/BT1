Confirmed root cause. The webhook `shop` and `topic` values consumed by `ShopifyAPI::Webhooks::Registry.process` come from HTTP headers (`shopify-shop-domain`, `shopify-topic`), while `HmacValidator.validate` only verifies `request.to_signable_string`, which is the raw body — the headers are never included in the signed content.

### Title
Webhook `shop`/`topic` cross-tenant spoofing via HMAC-unbound headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` and `topic` exclusively from HTTP headers, but the webhook HMAC only signs the raw body. `ShopifyAPI::Webhooks::Registry.process` trusts these header-derived fields when dispatching to the app's handler, so an attacker who owns any shop that has the same app installed (and therefore can trigger a genuinely-signed webhook delivery under the app's shared `client_secret`) can replay that valid body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header to impersonate a different, victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop`/`#topic` are read straight from unauthenticated headers [2](#0-1) . `Utils::HmacValidator.validate` computes and compares the HMAC only over `to_signable_string` (the body), never incorporating `shop` or `topic` [3](#0-2) . `Registry.process` checks only that this body HMAC is valid, then immediately builds `WebhookMetadata` using the header-derived, HMAC-unbound `request.topic` and `request.shop` before invoking the merchant's handler: [4](#0-3) . Because the app's webhook signing secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app — not scoped per shop — a valid `(raw_body, hmac)` pair captured from a webhook delivered for one shop remains cryptographically valid when replayed with a different `shopify-shop-domain` (or `shopify-topic`) header value. This breaks the intended binding: `shop_authenticated_by_hmac == shop_delivered_to_handler`.

### Impact Explanation
Host applications are documented to trust `data.shop` from `WebhookMetadata` as the tenant identifier for the event (see `docs/usage/webhooks.md`, which shows `data.shop` used directly to key per-shop processing) [5](#0-4) . An attacker who legitimately installs the target app on their own shop can obtain valid `(body, hmac)` pairs and replay them against the shared webhook endpoint with a forged `shopify-shop-domain` header naming a victim shop, causing the host app to process attacker-controlled webhook data/topic as if it originated from the victim tenant — a cross-tenant boundary violation.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged capability for any public/dev app) and observe one webhook delivery to capture a valid `(raw_body, hmac)` pair, then send an HTTP POST to the app's public webhook endpoint with modified headers. No secrets, tokens, or privileged access are needed.

### Recommendation
Bind `shop` and `topic` into the HMAC-covered signable content (or otherwise independently authenticate the header-derived `shop`/`topic` against the verified session/shop for that installation) before dispatching to the handler in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g. `orders/create`) and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify (valid under the app's shared `client_secret`).
3. Attacker resends that exact `(raw_body, hmac)` pair to the app's webhook endpoint, replacing the `X-Shopify-Shop-Domain` header with `victim.myshopify.com` (and optionally changing `X-Shopify-Topic`).
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) still succeeds because it only checks the body.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the handler with `shop: "victim.myshopify.com"`, `topic:` attacker-chosen — the host app processes attacker-controlled data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
