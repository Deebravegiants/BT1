Based on my investigation, I found a valid analog matching the bug class in the report: an identity field (`shop-domain`) that is acted upon but not cryptographically bound to the HMAC signature that authenticates the request.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value taken from an HTTP header that is never included in that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, entirely outside the signed material [2](#0-1) . `Registry.process` verifies the request using `Utils::HmacValidator.validate(request)`, which only checks `verifiable_query.hmac` against `to_signable_string` (i.e. the body) [3](#0-2) , and, once that passes, immediately forwards `request.shop` to the app's handler as the trusted tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) . `WebhookMetadata#shop` is documented as "The shop domain of the webhook" and is the field apps are expected to use to key which merchant's session/access token the webhook body applies to [5](#0-4) , and the official usage docs likewise instruct developers to route/enqueue work using `data.shop` [6](#0-5) .

The binding that should hold is: `hmac == HMAC(secret, body || shop || topic || ...)` so that `shop` is cryptographically tied to the specific delivery. Instead the gem only enforces `hmac == HMAC(secret, body)`, i.e. `shop` is verified against nothing. Because every shop installing the same app shares one `api_secret_key`, any tenant of the app (an "unprivileged" caller relative to *other* tenants) can capture a genuinely-signed webhook delivered to their own store, then resend the identical `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop. The HMAC check still passes because the header is not part of the signed content, and the handler processes the attacker-supplied body as if it originated from the victim shop.

### Impact Explanation
This breaks the tenant/shop identity binding that the app is meant to rely on for a signed webhook. An app that uses `data.shop` to select the corresponding merchant session/access token or to write tenant-scoped data (the documented and expected usage pattern) can be made to associate attacker-controlled webhook body content with a different, victim shop — a cross-tenant data-integrity/confusion issue reachable by any user who can install the app on their own store and capture one legitimate webhook delivery.

### Likelihood Explanation
Requires only that the attacker install the target app on a shop they control (a normal, unprivileged action) and be able to intercept/replay one legitimate webhook HTTP request they receive — no secrets, tokens, or privileged access are needed since HMAC signs only the body.

### Recommendation
Include the `shop-domain` header (and ideally `topic`/`webhook-id`) in the signed material verified by `HmacValidator`, or otherwise require the app to independently corroborate `request.shop` against a value bound to the signature (e.g., verify shop against a per-shop webhook secret if available, or reject when the header can't be tied to the HMAC).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Attacker triggers an event so Shopify sends a legitimately HMAC-signed webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches (shop header not included), so validation succeeds [7](#0-6) .
5. The handler receives `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)` and processes attacker-controlled data as belonging to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
