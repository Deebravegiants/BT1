### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` identity that is handed to the application handler is read from an unsigned HTTP header. This breaks the binding `hmac_verified(body) == shop_acted_on`, letting an attacker who can obtain one validly-signed webhook (e.g. by installing the app on their own store) replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` value to impersonate a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the signature purely off `verifiable_query.to_signable_string`, i.e. the raw body for webhook requests, and never touches the shop header: [4](#0-3) 

`Registry.process` only checks this body HMAC, then immediately forwards `request.shop` (the unverified header) to the application's handler as the trusted tenant identity: [5](#0-4) 

Because all webhooks for an app are signed with the same shared `api_secret_key` regardless of which shop triggered them, a valid `(raw_body, hmac)` pair obtained from a webhook delivered for shop A remains cryptographically valid for shop B — only the `shop-domain` header differs between deliveries, and that header carries no cryptographic binding. The documented handler contract explicitly trusts `data.shop` as the tenant identity for downstream business logic (e.g., `perform_later(shop_domain: data.shop, ...)`), so this untrusted field is exactly what apps are told to rely on.

### Impact Explanation
This crosses a tenant boundary without needing any of the app's credentials (`api_secret_key`, access tokens, etc.). An attacker only needs to be able to trigger one legitimate webhook delivery signed with the target app's secret — trivially achievable by installing the app on their own Shopify store and generating an event that fires a registered webhook topic (e.g. `products/update`). They then replay the identical raw body and HMAC to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop. The app's handler will process attacker-controlled webhook content believing it originated from the victim tenant, leading to cross-tenant data corruption or unauthorized actions scoped to another merchant's store — satisfying the "cross-tenant access" Critical impact criterion.

### Likelihood Explanation
Likelihood is Medium-High for any app that (a) has at least one publicly-installable listing or a way for the attacker to become a legitimate merchant using the same app instance, and (b) uses `data.shop` from `WebhookMetadata` to key any stateful action (as the docs recommend: `perform_later(shop_domain: data.shop, ...)`). No secret material, session, or access token is required — only the ability to become one tenant of a multi-tenant app and capture one raw HTTP request its own store receives.

### Recommendation
Include the shop identity (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signed body before trusting it (e.g., derive the shop from a separately-verified source such as the corresponding registered/active session rather than an unauthenticated header). At minimum, document that `WebhookMetadata#shop` is not covered by the signature and must not be used as an authorization boundary without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Install the target app on an attacker-controlled store `attacker-shop.myshopify.com`; trigger a webhook event (e.g. update a product) so Shopify delivers a webhook signed with the app's shared secret:
   - `POST /callback/products/update` with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Capture `B` and `H`.
3. Replay the exact same request to the app's public webhook endpoint, keeping `B` and `H` unchanged, but replacing the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only checks `HMAC(secret, B) == H` — still true — and passes. [6](#0-5) 
5. The registered handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)` and performs whatever business logic the app associates with that shop, even though the content actually originated from the attacker's own store.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
