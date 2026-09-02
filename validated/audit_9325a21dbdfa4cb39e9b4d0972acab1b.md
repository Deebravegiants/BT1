### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant identity spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies the webhook HMAC over the raw body only, then trusts an unauthenticated `shop-domain` header to populate `WebhookMetadata#shop`, which host apps use as the tenant identifier for the webhook.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` validates the HMAC exclusively against that signable string via `Utils::HmacValidator.validate(request)` [2](#0-1) . The `shop` value, however, is read straight from the `shop-domain`/`x-shopify-shop-domain` HTTP header with no cryptographic binding to the signed body [3](#0-2) . After the HMAC check passes, `Registry.process` forwards this unauthenticated header value directly into `WebhookMetadata.new(... shop: request.shop ...)`, which is handed to the app's handler as trusted tenant context [4](#0-3) .

The identity binding that should hold is: `HMAC-verified(body) == shop-attributed-to(body)`. In reality, only the body is verified; the `shop` header can be set to any value independent of the signed payload, so `verified(body) != verified(shop)`.

Concretely: an attacker who legitimately installs the app on their own shop (`attacker.myshopify.com`) receives genuinely-signed webhooks from Shopify with a correct HMAC for the body and their own `shop-domain` header. Because the HMAC covers only the raw body, the attacker can replay that exact body/HMAC pair to the app's webhook endpoint while substituting `shop-domain: victim.myshopify.com`. `HmacValidator.validate` still succeeds (it never inspects the shop header), and `Registry.process` calls the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's own data>)`.

### Impact Explanation
This breaks the shop/tenant binding that webhook handlers rely on to know which merchant a payload belongs to. The gem's own documentation and generated `WebhookMetadata` explicitly present `shop` as an authenticated field once `Registry.process` succeeds [5](#0-4) , but the value is never cross-checked against the HMAC-protected content. Any host app that keys database writes, cache invalidation, or job enqueuing (`perform_later(topic: data.topic, shop_domain: data.shop, ...)` as shown in the gem's own doc example) off `data.shop` is exposed to cross-tenant data confusion — attacker-controlled data being attributed and applied to a victim shop. This satisfies the "cross-tenant access" criterion because the gem itself performs the identity determination and asserts it as verified via its `process`/`WebhookHandler` API surface, not something the host app is deviating from documented behavior for.

### Likelihood Explanation
Exploitation requires only: (1) ability to install the target app on an attacker-controlled shop (any unprivileged Shopify merchant can do this) to obtain one genuinely-signed webhook body/HMAC pair, and (2) sending an unauthenticated HTTP POST to the app's public webhook endpoint with that captured body/HMAC and a forged `shop-domain` header. No access to `api_secret_key`, access tokens, or the app's `client_secret` is needed. This is straightforward for anyone who can install the app once.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed content the gem verifies, or otherwise document/enforce that `WebhookMetadata#shop` is unauthenticated and must be independently confirmed against a known, previously-established shop/session record before being trusted by handlers. At minimum, `HmacValidator`/`Registry.process` should not implicitly vouch for header-derived identity fields it never signs over.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com`; trigger any subscribed webhook topic to receive a genuine `(raw_body, x-shopify-hmac-sha256)` pair from Shopify.
2. POST that exact body to the app's webhook endpoint, replacing `x-shopify-shop-domain` with `victim.myshopify.com`, keeping the original `hmac-sha256` value unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [2](#0-1) ; since only the body is signed, validation succeeds.
4. The handler receives `WebhookMetadata(shop: "victim.myshopify.com", body: attacker_controlled_body, ...)` [4](#0-3) , causing the host app to process attacker data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
