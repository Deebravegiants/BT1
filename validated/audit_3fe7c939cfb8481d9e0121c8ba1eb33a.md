## Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content solely from the raw request body [1](#0-0) , while the `shop` identity used downstream by `Registry.process` to attribute the webhook to a specific tenant is read from an HTTP header that is never included in that signed content [2](#0-1) . This breaks the binding: `bytes verified` (raw body) ≠ `bytes acted on` (body + shop header), letting an attacker who possesses one valid app-secret-signed webhook (from their own shop, since the webhook HMAC secret is shared across all shops installing the app) relabel it to any victim shop.

### Finding Description
`Webhooks::Registry.process` validates the incoming request purely via `Utils::HmacValidator.validate(request)`:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
``` [3](#0-2) 

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` [4](#0-3) , and for `Webhooks::Request`, `to_signable_string` returns only `@raw_body`:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

Yet the `shop` value handed to the app's webhook handler comes from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is **not** part of the signed material:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

Because the webhook HMAC secret (`api_secret_key`) is the app's single client secret shared across every shop that installs the app, any shop installing the app will legitimately receive webhooks signed with this same secret. An attacker who installs the target app on their own store therefore holds a body+HMAC pair that is cryptographically valid for the shared secret, but that pair carries no cryptographic binding to *which* shop it came from — that binding lives only in the unauthenticated `shop-domain` header. The attacker can replay that body with the header rewritten to a victim shop's domain, and `HmacValidator.validate` will still pass, since it only checks the body bytes.

This is structurally identical to the referenced bug class: an operation (`handler.handle` attributing data to `shop`) uses a field (`shop`) that is not part of the cryptographically verified content (only `@raw_body` is verified), so the equality "verified identity == acted-upon identity" does not hold.

### Impact Explanation
This allows cross-tenant webhook injection: an attacker-controlled shop can forge webhook deliveries that the host application processes as though they originated from an arbitrary victim shop, because `WebhookMetadata.shop` is taken from the unauthenticated header while only the body is cryptographically verified [5](#0-4) . Depending on how the host app's webhook handler uses `shop` (e.g., updating shop-scoped state, triggering uninstall/data-deletion flows, billing/order processing), this can cause cross-tenant data corruption or unauthorized actions against a shop the attacker doesn't control — matching the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Exploitation requires the attacker to install the target app on a shop they control (a normal, low-privilege action available to any merchant/developer), capture one legitimately-signed webhook body+HMAC pair, and replay it to the app's public webhook endpoint with a modified `shop-domain` header. No access to the app's `client_secret`/`api_secret_key` value itself is required — only the ability to receive one webhook as an ordinary installer, which is inherent to using the app at all.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified signable content, or otherwise cross-check the header-derived `shop` against a value that is cryptographically tied to the specific installation before dispatching to handlers — e.g., include the shop domain in `to_signable_string`, or require callers to supply/verify the shop against a known active session for that shop before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`; the app registers a webhook (e.g., `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, and `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker intercepts/replays this request to the same endpoint, keeping body `B` and the HMAC header unchanged, but rewrites `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)` (unaffected by the header change) and returns `true` [4](#0-3) .
5. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` [5](#0-4) , causing the host application to process attacker-supplied webhook data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
