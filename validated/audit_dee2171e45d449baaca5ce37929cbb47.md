This confirms the vulnerability: the gem's documented API explicitly tells developers that `data.shop` in `WebhookMetadata` is "The shop domain of the webhook" [1](#0-0)  and shows the recommended handler pattern using `data.shop` as the tenant identifier for dispatching work (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [2](#0-1) , while `Registry.process` only checks `Utils::HmacValidator.validate(request)` before invoking the handler with `request.shop` [3](#0-2) .

### Title
Webhook shop-domain header is trusted as tenant identifier without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#shop` reads the tenant-identifying `shop-domain`/`x-shopify-shop-domain` HTTP header, but `HmacValidator` only signs `to_signable_string`, which returns the raw body alone. The `shop` header is never bound to the HMAC, yet the gem's documented API and `Registry.process` pass this unauthenticated value directly to the app's webhook handler as the trusted tenant key.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [4](#0-3) , and `Request#shop` is read straight from the `shop-domain` header with no relation to that body or its HMAC [5](#0-4) . `HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` [6](#0-5) . `Registry.process` gates only on this HMAC check and then forwards `request.shop` unchanged into `WebhookMetadata` for the handler [3](#0-2) .

The binding that should hold is:
`shop header value == shop that produced/authorized the signed body`

but the code only proves:
`HMAC(raw_body, api_secret_key) == received_signature`

The `shop` field is never part of the signed material, so it is "a field acted on but not covered by the HMAC." Any party that can produce one validly-signed body (e.g., the operator of their own Shopify store, who legitimately receives real signed webhook deliveries for their own shop) can replay that exact body to the victim app's webhook endpoint while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` dispatches the handler believing the event belongs to the attacker-chosen shop.

### Impact Explanation
This breaks the tenant boundary the gem purports to enforce: the documentation explicitly instructs developers to key per-shop work off `data.shop` [7](#0-6) . An attacker with a legitimately-signed webhook body from their own store can cause a merchant app to attribute that webhook's data (order/product/customer payload) to a different, victim shop by only changing the unauthenticated header — leading to cross-tenant data confusion/pollution in any app that follows the gem's documented pattern of trusting `data.shop`. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Any Shopify Partner can install their own app instance / operate their own development store, legitimately receive a correctly-HMAC-signed webhook body from Shopify for their own shop, then POST that identical body to the target app's public webhook callback URL with a forged `X-Shopify-Shop-Domain` header. No secrets, tokens, or privileged access are required — only the ability to receive one's own legitimate webhook and the public URL of the target's webhook endpoint (webhook paths are not treated as secret in this design). This is reachable purely through this gem's own `Request`/`Registry`/`HmacValidator` code paths and does not depend on the host app deviating from documented usage.

### Recommendation
Bind the shop domain into the verified material, e.g., include it (and other identity-relevant headers, such as `api-version`/`webhook-id`) in the signable string, or independently verify that the shop indicated by the payload/header matches a shop with an active, registered webhook subscription/session before dispatching. At minimum, document that `data.shop` is unauthenticated and must not be used as a sole tenant key without additional verification (such as matching against a known list of installed/authorized shops).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and registers for topic `orders/create`.
2. Shopify delivers a legitimately-signed webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(B, secret)`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same body `B` and HMAC header to the same app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` recomputes `HMAC(B, secret)` (only over `@raw_body`) and it matches — validation passes [8](#0-7) .
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` [9](#0-8) , causing the app to process attacker-controlled data under the victim shop's tenant context.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
