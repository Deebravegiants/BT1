### Title
Webhook `shop-domain` and `topic` are not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string using only the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that the body's HMAC matches, then hands the header-derived `shop` value straight to the app's webhook handler as trusted tenant identity — an identity binding break: `HMAC(body)` is verified, but `shop` (acted upon) is never part of what's verified.

### Finding Description
In `lib/shopify_api/webhooks/request.rb`: [1](#0-0) 

`shop` (`shopify_header("shop-domain")`) is read from headers, but `to_signable_string` returns only `@raw_body`. The HMAC validator in `lib/shopify_api/utils/hmac_validator.rb` computes the signature purely over `to_signable_string`: [2](#0-1) 

`Registry.process` then validates only this body HMAC before dispatching the header-derived `shop` (and `topic`) to the app's handler: [3](#0-2) 

The documented usage pattern explicitly trusts `data.shop` as the tenant identifier for downstream processing: [4](#0-3) 

**Broken equality**: the gem verifies `HMAC(secret, raw_body) == received_hmac`, but the consumer trusts `shop = header("X-Shopify-Shop-Domain")` as if it were `shop_that_produced(raw_body, received_hmac)`. Those are not the same value — the header is never covered by the signature.

### Impact Explanation
An attacker who has any shop connected to the app (a normal, unprivileged merchant/dev store) can trigger Shopify to deliver a legitimate webhook to the app's public callback endpoint, obtaining a valid `(raw_body, hmac)` pair signed with the app's real secret for their own shop. Because `shop-domain` is not part of the signed content, the attacker can then send that identical `(raw_body, hmac)` pair directly to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header swapped to an arbitrary victim shop domain. `Utils::HmacValidator.validate` still succeeds (body unchanged), and `Registry.process` forwards `shop: "victim-shop.myshopify.com"` with attacker-controlled `body` to the handler, exactly as recommended in the gem's own docs (`data.shop`, `data.body`). Any app that persists or acts on webhook data keyed by `data.shop` (the documented pattern) can have attacker-controlled data injected into another tenant's records — a cross-tenant access/data-integrity breach without any credentials beyond running one's own store.

### Likelihood Explanation
The webhook callback endpoint is by design a public, unauthenticated HTTP endpoint (Shopify does not restrict source IPs in most self-hosted deployments, and this gem provides no source verification beyond the body HMAC). Any user who can install/operate a shop using the target app can obtain a valid signed payload and replay it with a modified header — no secrets, tokens, or privileged access required.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) into the signed material, or otherwise cryptographically tie the header values to the verified body — e.g. include the shop domain in `to_signable_string`, or require the app to cross-check the header-derived shop against a shop known to have a currently active webhook registration/access token before trusting `data.shop`. At minimum, document prominently that `data.shop` is unauthenticated header data and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), causing Shopify to POST a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair to the app's callback URL.
2. Attacker crafts their own HTTP POST to the same callback URL using the identical `raw_body` and `X-Shopify-Hmac-Sha256` value captured/observed from step 1, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body`.
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, exactly as shown in `docs/usage/webhooks.md`'s example (`data.shop`, `data.body`), letting the attacker inject data attributed to a shop they do not control.

### Citations

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

**File:** docs/usage/webhooks.md (L19-30)
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
```
