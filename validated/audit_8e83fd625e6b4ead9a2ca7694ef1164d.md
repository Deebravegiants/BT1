This confirms the vulnerability: the webhook HMAC in this gem only covers the raw request body, while the `shop-domain`, `topic`, `api-version`, and `webhook-id` fields are taken directly from unauthenticated HTTP headers and passed through to the app's handler unverified.

### Title
Webhook `shop`/`topic` identity fields are trusted from unauthenticated headers while HMAC only covers the body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` in `Registry.process` only proves that the *body bytes* were signed with the app's secret [2](#0-1) . The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) via `shopify_header` [3](#0-2)  and are never part of the signed payload. `Registry.process` then hands `request.shop` straight into `WebhookMetadata` used by the host app's handler as the tenant identifier [4](#0-3) , and `WebhookMetadata.shop` is documented/typed as the trusted "shop domain of the webhook" [5](#0-4) .

### Finding Description
The intended equality the HMAC is supposed to guarantee is: `hmac == HMAC(secret, entire_webhook_identity_and_body)` binding shop+topic+body together for a specific tenant. In this gem the actual equality enforced is only `hmac == HMAC(secret, raw_body)` [6](#0-5) [1](#0-0) . Because `shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers that are not part of `to_signable_string`, any two webhook deliveries that happen to carry byte-identical bodies (which routinely happens for generic/no-payload topics such as `shop/redact`, `app/uninstalled`, or minimal JSON bodies) will produce the *same valid HMAC* regardless of which header values accompany them. An unprivileged actor who legitimately receives a webhook for their own store (e.g., by installing the target app on their own shop) can capture one valid `(body, hmac)` pair and replay it to the app's public webhook endpoint with an arbitrary `shop-domain` header claiming to be a victim shop. `HmacValidator.validate` still passes because it never inspects the header-derived fields [7](#0-6) , and `Registry.process` forwards the attacker-chosen `shop` value to the host application's handler as if Shopify had certified it [8](#0-7) .

### Impact Explanation
Applications that key tenant data lookups off `WebhookMetadata#shop` (the gem's own documented usage pattern, e.g., "shop_domain: data.shop" in `docs/usage/webhooks.md`) can be induced to process an event under the wrong tenant identity — e.g., triggering `shop/redact`/`customers/data_request`/`app/uninstalled` handling, cache invalidation, or state transitions for a shop the attacker does not own, using only a byte-identical replayed body. This is a cross-tenant identity confusion caused entirely by this gem's failure to bind the `shop` field into the HMAC-covered signable string, satisfying the "field acted on but not covered by the HMAC" analog class.

### Likelihood Explanation
Exploitability requires only: (1) being a merchant who has installed the target Shopify app on their own store (unprivileged, no special access), so they can legitimately receive one valid webhook delivery and its `X-Shopify-Hmac-Sha256` header, and (2) sending an HTTP request to the app's public webhook endpoint with that captured body/HMAC but a spoofed `X-Shopify-Shop-Domain` header. Many webhook topics (e.g., `shop/redact`, `app/uninstalled`, `customers/data_request`) have small or fixed body shapes, making body collisions across shops straightforward or even guaranteed.

### Recommendation
Include the header-derived identity fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-covered signable string, or otherwise cryptographically bind them to the body (e.g., validate `shop` against the session/shop the webhook was registered for, or require Shopify's newer signed webhook headers that cover these fields) before trusting `request.shop`/`request.topic` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate `shop/redact` (or any topic with an empty/fixed body such as `"{}"`) webhook with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` and a valid `X-Shopify-Hmac-Sha256`.
2. Attacker replays the identical raw body to the app's webhook endpoint but swaps the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, keeping the same body and HMAC.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` [1](#0-0)  — validation passes.
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop: "victim-shop.myshopify.com"` [8](#0-7) , causing the host app to act on the victim shop's tenant data based on an unauthenticated, attacker-controlled header value.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
