### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers. `Utils::HmacValidator` validates the HMAC solely against that raw body, so the `shop` value handed to the app's webhook handler is never bound to the signature that proves the request originated from Shopify.

### Finding Description
`Registry.process` validates a webhook purely by calling `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` and compares it to the `hmac-sha256` header value [1](#0-0) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or its signature [3](#0-2) .

After a successful HMAC check, `Registry.process` forwards this unauthenticated `shop` value straight to the app's handler as the tenant identity for the webhook payload: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) . The gem's own documentation tells integrators that `shop` in `WebhookMetadata` is "The shop domain of the webhook" and that `Registry.process` "will verify the request did indeed come from Shopify" [5](#0-4) [6](#0-5) , i.e. integrators are told they can trust `data.shop` as the tenant that owns `data.body`.

The broken identity binding is:
`HMAC-verified bytes (raw_body)` ⇎ `shop identity attributed to those bytes (shop-domain header)`

Because the header is outside the signed content, any two values of `shop-domain` produce the exact same valid signature for a given body.

### Impact Explanation
An unprivileged attacker who installs the target app on their own shop (Shop A) will legitimately receive a correctly-HMAC-signed webhook from Shopify for Shop A. The attacker can capture that raw body + HMAC and replay it to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header value with a victim shop's domain (Shop B). `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` dispatches the (attacker-controlled-origin) body to the handler labeled as belonging to Shop B. Any downstream logic that uses `data.shop` to select which tenant's records to update (the exact pattern shown in the gem's own docs, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will write/act on attacker-supplied data under another merchant's identity — a cross-tenant data-integrity/confusion issue reachable without any access token, `client_secret`, or privileged access.

### Likelihood Explanation
Any merchant/developer can install most public Shopify apps on a store they control, giving them a source of validly-signed webhook traffic and its secret-independent signature for arbitrary reuse. Capturing and replaying an HTTP POST with a modified header is trivial and requires no special access, TLS interception, or credential compromise — only network access to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed content that is verified, or otherwise cryptographically bind the `shop-domain` header to the HMAC before trusting it in `WebhookMetadata`. At minimum, document/enforce that `Registry.process` must also validate that the `shop` on the request matches an app-tracked list of shops with an active webhook registration/session before dispatching to handlers.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw POST body plus its `X-Shopify-Hmac-Sha256` and `X-Shopify-Shop-Domain` headers.
2. Replay the exact same body and HMAC header to the app's webhook endpoint, replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` returns `true` because it only hashes `raw_body` [7](#0-6) ; `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and the attacker's body, even though the payload never originated from that shop.

### Citations

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
