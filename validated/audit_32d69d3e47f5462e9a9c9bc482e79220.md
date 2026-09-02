This confirms the finding. The gem's own documentation states that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and that `data.shop` — "The shop domain of the webhook" — is a trusted field handed to the app's handler [2](#0-1) . But the HMAC verification only covers the raw body, not the `shop-domain` header that `data.shop` is derived from.

### Title
HMAC verification in `ShopifyAPI::Webhooks::Registry.process` does not bind the `shop` field, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#shop` is read directly from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) HTTP header [3](#0-2) , while `Utils::HmacValidator.validate` only checks the HMAC against `to_signable_string`, which returns solely `@raw_body` [4](#0-3) . The `shop` header is never included in the signed content, so the HMAC check in `Registry.process` [5](#0-4)  validates only that the body bytes match the app's shared `client_secret`, not which shop the webhook actually belongs to.

### Finding Description
The equality the code implicitly assumes is:

`shop bound by HMAC signature == shop delivered to WebhookHandler#handle`

But the actual behavior is:

`HMAC covers only raw_body (Request#to_signable_string)` ≠ `shop comes from an unsigned header (Request#shop)`

Since a Shopify app uses **one shared `client_secret`/`api_secret_key` for all shops** that install it, the HMAC computed over the body is identical regardless of which tenant the webhook is "for." An unprivileged internet user who controls (or has installed) the app on their own shop can:

1. Trigger any webhook topic on their own shop (attacker-owned tenant, e.g. `attacker.myshopify.com`) and capture the legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair that Shopify sends to the app's callback URL.
2. Replay that exact request to the same webhook endpoint, only modifying the `X-Shopify-Shop-Domain` header to name a victim shop (e.g. `victim.myshopify.com`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5) , which passes because it only recomputes HMAC over `raw_body`, unaffected by the header change.
4. `Registry.process` then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [7](#0-6)  using the attacker-controlled `shop` value, and invokes the host app's `handler.handle(data:)` with it.

The documented contract of this gem is that `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  before invoking the handler, and that `data.shop` is "the shop domain of the webhook" [2](#0-1) . In reality, only the body's authenticity is verified — the shop identity is not cryptographically bound at all, so the gem hands the host app's handler a `shop` value under attacker control despite claiming the request has been verified.

### Impact Explanation
This is a cross-tenant identity binding break. A host application that follows the gem's documented contract and uses `data.shop` from a verified webhook (e.g., to key data updates, trigger fulfillment actions, or attribute events to a shop record) can be tricked into applying attacker-supplied webhook content to an arbitrary victim shop identifier, since the "verified" `shop` field is actually unauthenticated. This falls under the Critical "cross-tenant access" impact category, because it lets one tenant (the attacker's own shop) inject data or trigger actions attributed to another tenant (the victim shop) purely by replaying a request they legitimately received and modifying an unsigned header.

### Likelihood Explanation
Any merchant/developer who installs the target app on their own store can generate arbitrary legitimately-signed webhook bodies for topics they control (e.g., by updating a product, placing/cancelling an order, etc.), then replay the request to the app's public webhook endpoint with a forged `Shop-Domain` header. No secrets, tokens, or privileged access are required — only the ability to receive a real webhook once and to send an HTTP request to the app's callback route, which is by design an unauthenticated public endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed content check, or independently validate that `request.shop` corresponds to a shop that is actually expected to be able to send the topic/body received (e.g., cross-check against a shop-specific secret, an installed-shop registry, or bind the `shop` header into `to_signable_string` before verifying). At minimum, document clearly that `data.shop` is not cryptographically authenticated and must not be trusted by host applications without additional verification against known installed shops.

### Proof of Concept
```ruby
# Attacker owns/installs the app on their own shop "attacker.myshopify.com"
# Step 1: Attacker triggers a webhook (e.g., orders/create) and captures the raw POST:
#   raw_body = '{"id":123,"note":"hi"}'
#   headers  = {
#     "X-Shopify-Topic" => "orders/create",
#     "X-Shopify-Hmac-Sha256" => "<valid-hmac-of-raw_body-with-shared-secret>",
#     "X-Shopify-Shop-Domain" => "attacker.myshopify.com"
#   }

# Step 2: Attacker replays the exact same body+hmac, changing only the shop header:
forged_headers = headers.merge("X-Shopify-Shop-Domain" => "victim.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Step 3: HMAC validation still succeeds because it only checks raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Step 4: Registry.process invokes the handler with shop: "victim.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
# WebhookHandler#handle receives data.shop == "victim.myshopify.com" even though
# the content originated from and was signed for "attacker.myshopify.com".
```

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
