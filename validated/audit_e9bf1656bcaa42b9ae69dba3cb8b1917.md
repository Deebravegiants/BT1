This confirms the vulnerability pattern precisely matches the rules' criterion: "a field acted on but not covered by the HMAC."

### Title
Webhook `shop-domain` header is trusted for tenant routing but excluded from HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body [1](#0-0) , while the `shop` identity value that the registry later trusts for tenant attribution is read straight from an unauthenticated HTTP header [2](#0-1) . `Registry.process` verifies only that HMAC before dispatching `request.shop` into the handler as the tenant identity [3](#0-2) .

### Finding Description
The identity binding that should hold is: `bytes verified by HMAC == bytes the shop identity is derived from`. Here that equality is broken. `HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for a webhook `Request` returns solely `@raw_body` [1](#0-0)  and `lib/shopify_api/utils/hmac_validator.rb` lines 26-31. The `shop`, `topic`, `api-version`, and `webhook-id` values used downstream are all pulled from HTTP headers via `shopify_header`, none of which are included in the signed string [4](#0-3) .

`Registry.process` raises only if the HMAC over the body is invalid, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` header value and hands it to the app's registered handler as the trusted tenant identifier [3](#0-2) .

Because the header is never bound to the signed payload, any party who has previously obtained one valid `(body, hmac)` pair signed under the app's `client_secret` — for example, by owning a legitimate installed shop and receiving a real webhook delivery to their own endpoint — can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header for a different (victim) shop. The HMAC still validates because it only covers `@raw_body`, and the handler is invoked believing the data belongs to the victim's shop.

### Impact Explanation
This breaks the shop-authenticated-as identity equality: `shop asserted to the HMAC != shop delivered to the handler`. If an app's webhook handler uses `WebhookMetadata#shop` to look up per-tenant state, credentials, or to write data scoped by shop, this analog allows cross-tenant data confusion/access — an attacker-controlled shop identity is accepted as if the merchant genuinely owning it sent the webhook, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high relative to cost: the attacker only needs one legitimate webhook delivery from their own (attacker-owned) shop installation — which they can trivially generate by installing the app and triggering any subscribed event — to obtain a valid `(body, hmac)` pair. They can then replay that same pair to the app's public webhook endpoint with a forged `shopify-shop-domain` header pointing at any victim shop, with no need for the app's `client_secret` or any privileged credential.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signed string that `to_signable_string` returns (or otherwise cryptographically bind them to the payload), so `HmacValidator.validate` fails whenever any of these headers are altered, not just when the raw body changes.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; a real webhook fires, delivering body `B` and header `shopify-hmac-sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker captures `(B, H)`.
3. Attacker sends a POST to the app's public webhook endpoint with body `B`, header `shopify-hmac-sha256: H` (unchanged, still valid), but `shopify-shop-domain: victim-shop.myshopify.com` and any desired `shopify-topic`/`shopify-webhook-id`.
4. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)` — passes, because validation only checks `B` against `H` [5](#0-4) .
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built with `shop = "victim-shop.myshopify.com"` and passed to the app's handler as trusted data [6](#0-5) , despite the payload actually originating (and being signed) for `attacker-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
