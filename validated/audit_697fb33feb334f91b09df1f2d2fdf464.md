This confirms the finding: the gem's own documentation states that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and explicitly documents `data.shop` as "The shop domain of the webhook" that handler code is expected to trust and act on (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [2](#0-1) . But the HMAC verification performed by the gem only covers the raw request body, never the `shop-domain` header.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, while the `shop` identity exposed to the app's handler is read from an unauthenticated HTTP header. This breaks the binding: `shop claimed in X-Shopify-Shop-Domain header == shop cryptographically bound to the signed payload`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `#hmac` is decoded from the `hmac-sha256` header [4](#0-3) . `#shop` is a *separate* accessor that just reads the `shop-domain` header, uncorrelated with the signed content [5](#0-4) .

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the received signature [6](#0-5) . It never incorporates `shop`, `topic`, `webhook_id`, or `api_version` headers into the signed material.

`Webhooks::Registry.process` raises only if this body-only HMAC check fails, then immediately forwards `request.shop` (the unauthenticated header) to the app's handler as the authoritative tenant identity: [7](#0-6) .

Because every shop installed on the same app shares the same `api_secret_key` (`Context.api_secret_key` is a single, app-wide secret, not per-shop), any shop where the attacker's app is installed can receive a *validly HMAC-signed* webhook for their own tenant. Since the `shop-domain` header is excluded from the signed content, the attacker can replay that same body+HMAC pair to the victim app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (the body and HMAC are untouched and valid), and `Registry.process` calls the handler with `shop: <victim-shop>` [8](#0-7) , causing the app to attribute attacker-controlled webhook data to a different merchant's tenant.

### Impact Explanation
This is a cross-tenant confusion: an unprivileged attacker who controls one shop's installation of the app can cause the host application to process webhook data under a victim shop's identity, since the gem's documented contract explicitly instructs developers to trust `data.shop` as "The shop domain of the webhook" once `Registry.process`/`HmacValidator.validate` return successfully. Any app that keys per-tenant side effects (billing, inventory sync, order creation, cache invalidation, feature flags) off `data.shop` is exposed to cross-tenant data corruption purely through this gem's verification logic, matching the High-severity "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high for any developer following the documented usage exactly as shown in `docs/usage/webhooks.md`: the gem gives no signal that `shop` is any less trustworthy than the verified body, and no separate API is offered to bind `shop` into the HMAC check. Exploitation requires only that the attacker control (or install the target app on) at least one shop — an ordinary, unprivileged action available to any merchant/developer — and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is trivial.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`api-version`) header value in the HMAC-signed material, or otherwise cryptographically bind them to the verified body, before exposing them to the handler as trusted identity fields. At minimum, document prominently that `data.shop` is not verified by `HmacValidator` and must be independently authenticated (e.g., cross-checked against a shop already known to have a valid session/webhook subscription) before being used for tenant-scoped operations.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and triggers a webhook (e.g. orders/create), producing a genuine payload:
raw_body = '{"id": 1, "note": "hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
hmac_b64 = Base64.encode64(hmac)   # valid signature for raw_body under the app's shared secret

# 2. Attacker replays the same body+hmac to the app's public webhook endpoint,
#    but swaps the shop-domain header to a victim shop they do NOT control:
POST https://victim-app.example.com/webhooks/orders_create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <hmac_b64>
X-Shopify-Shop-Domain: victim-shop.myshopify.com   # attacker-controlled, unverified
Body: {"id": 1, "note": "hello"}

# 3. ShopifyAPI::Webhooks::Registry.process(request) succeeds:
#    - Utils::HmacValidator.validate(request) passes (body+hmac match)
#    - handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
#    The victim app now processes attacker-supplied order data as belonging to victim-shop.
```

### Citations

**File:** docs/usage/webhooks.md (L12-26)
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
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
