### Title
Webhook shop/topic/api-version/webhook-id headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` treats a passing `Utils::HmacValidator.validate(request)` check as proof the *entire request*, including these header-derived fields, "did indeed come from Shopify" (as literally documented in `docs/usage/webhooks.md`), but the signature only binds the body bytes. This breaks the identity equality `verified_bytes == trusted_shop`, since `shop` is a field acted on but never included in the HMAC-signed payload.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic tie to the signed body: [3](#0-2) 

`Registry.process` gates on the HMAC check and then forwards the unauthenticated `request.shop` (and other header fields) straight into `WebhookMetadata`, which is handed to the app's handler as trusted tenant-identifying data: [4](#0-3) 

The gem's own documentation instructs developers to trust `data.shop` as the authenticated tenant identifier once `Registry.process` succeeds, and explicitly claims the call "will verify the request did indeed come from Shopify": [5](#0-4) [6](#0-5) [7](#0-6) 

Because `shop` is not part of the signed bytes, any party that has legitimately received one valid `(raw_body, hmac)` pair for their own store (e.g., any merchant who installed the app — an unprivileged actor relative to other tenants) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still returns `true` because it only checks the untouched body, so `Registry.process` accepts the request and reports the attacker-chosen `shop` value to the handler as if Shopify had certified it.

### Impact Explanation
This is a cross-tenant identity-binding break: the equality the library implicitly guarantees — "HMAC verified ⇒ all fields of the webhook request, including `shop`, are authentic" — does not hold, since only `raw_body` is signed. A host app that follows the gem's documented pattern (using `data.shop` to key per-tenant records, as shown in the gem's own example) can be made to apply shop A's real webhook body content under an attacker-chosen shop identifier, corrupting or exposing cross-tenant data association. This falls under the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any actor able to install the app on a store of their own (a normal unprivileged onboarding flow, not requiring `api_secret_key`, access tokens, or TLS interception) will legitimately receive Shopify webhooks with valid `(raw_body, hmac)` pairs. Replaying those bytes with modified `shop`/`topic`/`webhook_id` headers directly to the app's public webhook URL is trivial and requires no secret material — the attacker only needs a plain HTTP client. Likelihood is high wherever a host app implements the documented `data.shop`-based tenant routing pattern.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload used by `to_signable_string`, or otherwise cryptographically bind them to the raw body before exposing them via `Request#shop`/`#topic`/etc. At minimum, update `Registry.process` and the documentation to make clear that only body integrity is verified and that `shop` must be independently corroborated against a known, previously established session/tenant record before being used as a trust boundary.

### Proof of Concept
1. App merchant "shop-a.myshopify.com" installs the target app and receives a legitimate webhook: `raw_body = '{"id":123,...}'`, `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
2. Attacker (this merchant) captures the request and resends it to the app's public webhook endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` identical but changing `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only reflects `raw_body`, which is unchanged.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <shop-a's data>, ...))`, so the host application processes shop A's webhook body under shop B's identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
