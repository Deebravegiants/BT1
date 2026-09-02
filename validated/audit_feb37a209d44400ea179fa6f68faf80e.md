This confirms the root cause: the webhook HMAC signature only covers the raw body, while the `shop` value used for tenant identification is taken from an unsigned HTTP header.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` (tenant identifier) is read from a separate, unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then trusts the header-derived `shop` value when dispatching to the app's handler, breaking the intended binding between "the HMAC-authenticated payload" and "the shop that payload is attributed to."

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signed content [2](#0-1) . `Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e., body only) and, if valid, immediately builds `WebhookMetadata` using `request.shop` from the header, then dispatches it to the app's registered handler [3](#0-2) .

The equality that should hold is: `shop authenticated by HMAC == shop delivered to the handler`. In reality, the HMAC only authenticates `body == signed_body`; it says nothing about which shop that body/HMAC pair was issued for. Any party who receives a legitimately signed webhook from Shopify for one shop (e.g., an attacker's own store, which any unprivileged merchant can create) possesses a valid `(raw_body, hmac)` pair. That party can replay this exact `raw_body`/`hmac` to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (e.g., a victim's `*.myshopify.com` domain). `HmacValidator.validate` will succeed because it never inspects the shop header, and `Registry.process` will hand the attacker-controlled `shop` string straight to `WebhookMetadata.shop`, which apps are documented to use as the tenant key for their own persistence/business logic [4](#0-3) , e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` as shown in the gem's own documented handler example [5](#0-4) .

This is the same class of bug as the report's settings-key collision: an input value is trusted and acted upon (here, `shop`) without being cryptographically bound to the field that establishes trust (the body HMAC).

### Impact Explanation
This breaks the tenant (shop) boundary that apps rely on this gem to correctly establish before processing a webhook. Because the gem is what parses headers and validates the HMAC, and its own documented pattern is to key persistence and business logic off `WebhookMetadata.shop`, any application following the gem's documented usage inherits a cross-tenant confusion: attacker-controlled body content (from a webhook belonging to a shop the attacker controls) gets attributed to and processed under a victim shop's identity. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Requires only an attacker to run a normal Shopify development/trial store (freely available to any unprivileged internet user), capture a genuinely-delivered webhook (raw body + `hmac-sha256` header) for their own store, and replay it to the target app's public webhook endpoint with a forged `shop-domain` header. No access to the app's `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Include the shop domain (and other identifying headers, e.g., topic, webhook id) as part of the HMAC-signable content, or otherwise cryptographically bind the header-derived `shop` to the verified request, e.g., by validating that the shop the HMAC was verified for matches a shop the app has previously confirmed/installed via the associated topic/webhook id, or by having `to_signable_string` incorporate a canonicalized combination of the shop header and body so that tampering with the header invalidates the HMAC.

### Proof of Concept
1. Attacker creates their own Shopify store `attacker-shop.myshopify.com` and installs the target app, registering a webhook (e.g., `orders/create`).
2. Attacker triggers the webhook and Shopify delivers a POST with body `B` and header `shopify-hmac-sha256: H` (valid HMAC of `B` computed with the app's shared secret) and `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends this exact `B`/`H` pair to the app's webhook endpoint, replacing only the `shopify-shop-domain` header with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
