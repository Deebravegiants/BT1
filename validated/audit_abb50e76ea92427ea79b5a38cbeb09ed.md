### Title
Webhook HMAC signs only the raw body, not the `shop-domain`/`topic`/`webhook-id` headers, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (used in `Registry.process`) only authenticates the request body bytes. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are read directly from attacker-controllable input and passed unauthenticated into `WebhookMetadata`, which the host app's `WebhookHandler#handle` trusts as the tenant/topic identity.

### Finding Description
The identity binding that should hold is:
`hmac == HMAC(client_secret, shop ‖ topic ‖ body)` (i.e., the signature should bind the tenant/topic/body triple).

Instead, the gem implements:
`hmac == HMAC(client_secret, body)` only [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding [2](#0-1) .

`Registry.process` validates only this body-only HMAC and then forwards the unauthenticated `shop`/`topic`/`webhook_id` values straight into the handler: [3](#0-2) .

`WebhookMetadata.shop` and `.topic` are then consumed by the host application's handler as the authoritative tenant/topic identity, as shown in the gem's own documentation example that dispatches background jobs keyed on `data.shop` and `data.topic`: [4](#0-3) .

Because the HMAC never covers `shop`/`topic`, an attacker who has *any* one legitimate `(raw_body, hmac)` pair — for example from a webhook Shopify sent to their own installed/dev-store app for any topic — can resend the exact same body+HMAC directly to the app's public webhook endpoint while substituting arbitrary `shopify-shop-domain` and `shopify-topic` header values. `HmacValidator.validate` will still succeed because it never inspects those headers [5](#0-4) .

### Impact Explanation
This breaks the tenant/topic binding that `WebhookHandler` implementations are documented and expected to rely on. An attacker can make the app process a webhook it believes originated from a different shop (`data.shop`) and/or under a different topic (`data.topic`) than what Shopify actually signed. If the host app uses `data.shop` to select which tenant's records to update/delete (a common and gem-documented pattern), or dispatches to different logic branches based on `data.topic` — including the mandatory GDPR topics `customers/redact` and `shop/redact` that this gem special-cases [6](#0-5)  — this enables cross-tenant data confusion/corruption using only a body+HMAC pair the attacker legitimately obtained for their own shop.

### Likelihood Explanation
Requires only: (1) the attacker owning/installing the target app on any shop (including a free dev store) to legitimately receive one real webhook, and (2) the ability to POST directly to the app's public webhook endpoint with custom headers — both trivial for an unprivileged internet user, no `client_secret` or access token needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed/verified material for webhook requests, or otherwise cryptographically bind them (e.g., verify header values against a separately fetched/registered mapping) before constructing `WebhookMetadata`, mirroring the report's recommendation to ensure all identity-relevant fields contribute to the verified signature rather than being trusted independently of it.

### Proof of Concept
1. Attacker installs the target Shopify app on Shop A (their own dev store) and registers for any webhook topic (e.g., `products/update`).
2. Shopify sends a legitimate webhook to the attacker's endpoint: `raw_body=B`, headers include `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: products/update`.
3. Attacker crafts a new HTTP POST to the same app endpoint with identical `raw_body=B` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: customers/redact`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed and passed to `Registry.process`.
5. `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only returns `B`, which is unchanged [1](#0-0) .
6. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...))` [7](#0-6) , causing the app to act on `victim-shop.myshopify.com` under a topic and body the attacker fully controls, despite passing HMAC validation.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
