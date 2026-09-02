Based on my investigation, I've confirmed the root cause. Here is the analog finding:

### Title
Webhook Shop Attribution Bypass via Unsigned `shop-domain` Header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies only that the HMAC signature matches the raw request body, but the `shop` field passed to the app's webhook handler is read from an HTTP header that is never included in the signed content. This breaks the identity binding "shop authenticated == shop attributed to the webhook data," allowing a party that possesses one validly-signed webhook body/HMAC pair to relabel that payload as belonging to any other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signature [2](#0-1) .

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `to_signable_string` (i.e., the raw body) and compares it to the `hmac` header [3](#0-2) . If validation succeeds, `Registry.process` immediately builds `WebhookMetadata` using `request.shop`, the unauthenticated header value, and forwards it to the app-supplied handler [4](#0-3) . `WebhookMetadata#shop` is a plain `String` field with no additional verification [5](#0-4) .

Equality that should hold but doesn't: `hmac_verified_bytes == bytes_that_determine_tenant`. Here, `hmac_verified_bytes = raw_body` while `bytes_that_determine_tenant = shop-domain header`, which are disjoint. Any party who can produce one legitimately HMAC-signed `(raw_body, hmac)` pair — for example a merchant who installed the app and thus receives genuine Shopify webhooks for their own shop — can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still succeeds (body/HMAC unchanged), but `Registry.process` and the downstream handler attribute the payload to the attacker-chosen victim shop, per the documented handler contract in `docs/usage/webhooks.md` (`data.shop` is described as "The shop domain of the webhook" and is expected to be trusted by host apps to route/store data) [6](#0-5) .

This is the direct analog to the reported bug class: just as `set_service` trusted `vault_params` without verifying the depositor actually owned the stake (an unchecked identity binding), `Registry.process` trusts the `shop` header without verifying it is bound to the signed body.

### Impact Explanation
This allows cross-tenant data injection/corruption: an attacker who legitimately controls one Shopify shop with the app installed can cause the app to process genuine, validly-signed webhook payloads under a different, victim shop's identity. Depending on how the host app uses `data.shop` (as most apps do per the documented pattern of `shop_domain: data.shop`), this can lead to writing/deleting/updating another tenant's records, corrupting per-shop caches, or triggering shop-scoped side effects (e.g., inventory sync, order fulfillment actions) against a shop the attacker does not control — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own shop has the app installed and receives at least one real webhook (trivial — attacker can trigger events on their own store), and (2) the attacker can send arbitrary HTTP requests with custom headers to the app's public webhook endpoint (trivial for any internet-reachable webhook route). No access to `api_secret_key`, tokens, or privileged accounts is needed, making this a realistically reachable, low-effort attack path for any unprivileged Shopify merchant.

### Recommendation
Bind the shop identity into the verified signature material, or independently verify `shop-domain` against Shopify's known tenant list before trusting it. Concretely, include the `shop-domain` (and ideally `topic`, `webhook_id`, `api_version`) header values in `to_signable_string`, or perform a secondary authenticated lookup (e.g., confirm the shop has an active, previously-established session/webhook registration matching this specific `webhook_id`) before invoking the handler with that shop attribution. At minimum, document that host apps must not solely rely on `data.shop` for tenant attribution without additional verification, though the more robust fix is in `Request#to_signable_string`/`HmacValidator`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real event (e.g., updates a product), causing Shopify to send a legitimately HMAC-signed webhook to the app's endpoint:
   ```
   POST /callback/products/update
   X-Shopify-Topic: products/update
   X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: 123
   X-Shopify-Api-Version: 2024-01
   <raw_body>
   ```
2. Attacker captures this exact `(raw_body, X-Shopify-Hmac-Sha256)` pair (they own the shop, so this is trivial — they can even sniff their own traffic or reuse a webhook replay tool).
3. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` header to the same endpoint, but sets:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only, which still matches, so validation passes [3](#0-2) .
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and calls the app's handler, which (per the documented usage pattern) processes/stores this data as belonging to `victim-shop.myshopify.com` [4](#0-3) .

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
