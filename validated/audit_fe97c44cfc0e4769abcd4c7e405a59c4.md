### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` is computed only over the raw request body [1](#0-0) . The header carrying the shop identity is never part of the signed material, so the binding "HMAC-verified bytes == bytes the handler trusts as this shop's data" does not hold.

### Finding Description
`Registry.process` verifies a webhook request purely via `Utils::HmacValidator.validate(request)` [2](#0-1) , and `HmacValidator` computes the signature over `verifiable_query.to_signable_string` [3](#0-2) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated headers [4](#0-3) .

After a successful HMAC check, `Registry.process` builds `WebhookMetadata` directly from `request.shop` (and the other header-derived fields) and hands it to the host application's handler as the trusted tenant identity [5](#0-4) . Because `client_secret` (used as the HMAC key) is per-app, not per-shop, any body+HMAC pair that is valid for one installed shop is *also* a valid HMAC for that same body under any other header set, since the header content is never mixed into the signed string. This breaks the identity binding: `shop authenticated == shop bytes acted on`.

### Impact Explanation
This lets a merchant who has installed the app on their own shop capture a genuine Shopify-issued webhook (body + valid `X-Shopify-Hmac-SHA256`) and replay it against the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop domain. The gem's `Registry.process` will accept it as authentic (HMAC still validates against the untouched body) and dispatch `WebhookMetadata.new(shop: <attacker-controlled victim shop>, ...)` to the app's handler, which typically uses `shop` to look up the victim's session/store data and act on it — a cross-tenant data/action confusion in a Rails/Sinatra host built on this gem's documented `Registry.process` contract. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is limited by the fact that an attacker must possess at least one genuine, valid webhook (body + HMAC) — obtainable trivially by installing the app on their own store and triggering any subscribed webhook topic (e.g., `orders/create`) with attacker-chosen content. No secret, access token, or privileged account is required beyond becoming a legitimate app user, which is available to any unprivileged internet user who installs a public/embedded app. The replay itself is a simple unauthenticated HTTP POST to the app's public webhook route with the header rewritten.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the material that is HMAC-verified, or otherwise cryptographically bind them to the body before dispatch — e.g., have `Webhooks::Request#to_signable_string` return a canonical concatenation of the raw body with these header values, and require the host app / gem to recompute and compare against a signature that Shopify issues over that same canonical string. If Shopify's own webhook signature by design only covers the body (which matches real Shopify Admin webhook behavior), then the gem should not treat `shop` as authenticated purely by header value; it should require the caller to correlate `request.shop` against an existing, independently-verified session for that shop before trusting the tenant identity in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; subscribe to any HTTP webhook topic.
2. Trigger the topic so Shopify sends a genuine webhook: body `B`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, header `X-Shopify-Hmac-Sha256: HMAC(client_secret, B)`.
3. Capture the raw POST, replace `X-Shopify-Shop-Domain` with `victim.myshopify.com` (and optionally the topic header to match a topic that exists for the victim), keep body `B` and the HMAC header unchanged.
4. POST this modified request to the app's webhook endpoint.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` — identical to the captured HMAC — so validation passes [2](#0-1) .
6. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)` [6](#0-5)  and processes attacker-controlled data under the victim shop's identity, despite the "shop" claim never having been part of the verified signature.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
