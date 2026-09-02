### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted from unauthenticated HTTP headers and are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never included in the signed content. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands these unauthenticated header values straight to the app's webhook handler as trusted metadata. This breaks the identity binding: `hmac == HMAC(secret, body)` is verified, but `shop` (the tenant identifier passed to the handler) is not bound to that HMAC at all.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with no cryptographic binding to the HMAC and no additional sanitization/whitelisting (e.g. via `ShopValidator`, which exists in the gem but is never invoked here): [2](#0-1) 

`Registry.process` validates the HMAC against the body, then immediately forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to the app-supplied handler as if they were verified: [3](#0-2) 

The documented usage pattern explicitly encourages apps to key their tenant-scoped work off `data.shop` directly, with no additional verification step suggested: [4](#0-3) 

The equality the gem implicitly claims to guarantee is:
`hmac_valid == true` implies `(shop, topic, webhook_id, api_version, body)` all genuinely originated from Shopify for that shop.

What is actually guaranteed is only:
`hmac_valid == true` implies `body` was HMAC-signed with the app's secret — nothing about `shop`, `topic`, `webhook_id`, or `api_version`.

Because the webhook signing scheme is body-only, any party capable of obtaining one valid `(raw_body, hmac)` pair for the app's `client_secret` (e.g., by owning/controlling a shop that installs the same app and receiving that shop's own legitimate webhook) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a different, victim shop. `HmacValidator.validate` will still succeed because it only checks the body against the HMAC, and `Registry.process` will pass the forged `shop` value through to the handler unchanged.

### Impact Explanation
If the host application follows the gem's own documented pattern of trusting `data.shop` to select which tenant's data to update in response to a webhook (exactly as shown in `docs/usage/webhooks.md`), an attacker who controls one shop installed on the app can forge webhook deliveries that are processed as if they belong to an arbitrary victim shop domain of the attacker's choosing, while the actual signed body content originated from the attacker's own shop. This is a cross-tenant identity confusion enabled purely by a gap in what the gem's own `HmacValidator`/`Webhooks::Request` binds, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The precondition — obtaining one legitimately signed `(raw_body, hmac)` pair — is trivially satisfiable by any developer/attacker who installs the target app on their own (free) development shop; every subsequent webhook delivery to that installation naturally supplies such a pair. Replaying it with a substituted `shop`/`topic` header requires only unprivileged control over an HTTP client hitting the app's public webhook endpoint — no access token, `client_secret`, or TLS interception is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (not just the raw body) in the HMAC-signable string used by `Utils::VerifiableQuery`/`HmacValidator` for webhook requests, or at minimum require host applications to independently verify `request.shop` against the set of shops they know to have installed the app and to whom the specific `webhook_id`/topic was actually registered, before trusting `WebhookMetadata#shop` for tenant-scoped operations. Document this gap clearly if the header fields will remain unauthenticated by design.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and registers for a webhook topic (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this exact `(B, hmac)` pair (they control the receiving server or can sniff/log it since it's their own installation).
4. Attacker resends the same body `B` and `hmac` header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the HMAC: [5](#0-4) 
6. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the app processes attacker-controlled body content under the victim shop's tenant context.

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

**File:** docs/usage/webhooks.md (L12-29)
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
