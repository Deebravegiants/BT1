### Title
Webhook HMAC covers only the raw body, not the `shop-domain` header — the `shop` identity used by handlers is unauthenticated - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC and then dispatches to the registered handler using `request.shop`, `request.topic`, etc. But the HMAC signature is computed exclusively over the raw request body; every other identifying field pulled from HTTP headers — most importantly `shop`, which tenant-scoped handlers use to decide which merchant's data to act on — is never part of the signed bytes. This is the same "field acted on but not covered by the HMAC" defect pattern as the reported base-amount bug: the binding `authenticated(shop) == acted_on(shop)` is broken because only the body, not the shop, is authenticated.

### Finding Description
`Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic tie to the HMAC: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute and compare the signature strictly against `verifiable_query.to_signable_string` (i.e., the body only): [3](#0-2) 

`Registry.process` checks that HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

Equality that should hold but doesn't:
`hmac_signed_bytes == bytes_that_determine_which_shop_the_event_is_attributed_to`

Before the attacker's action: for a legitimate webhook, `shop-domain` header happens to match the shop that actually owns the body/HMAC, purely because Shopify's own servers set both consistently.
After the attacker's action: an unprivileged internet user who can obtain any one valid `(raw_body, hmac)` pair signed with the app's secret (e.g., by installing the app on their own store and capturing their own legitimate webhook delivery, which is normal, unprivileged access to their own data) can replay that exact body/HMAC pair to the app's public webhook endpoint while swapping the `shopify-shop-domain` header to any other value. `HmacValidator.validate` still returns `true` (it only checks the body), so `Registry.process` proceeds and calls the handler with `WebhookMetadata#shop` set to the attacker-chosen value instead of the shop that actually generated the signed payload.

### Impact Explanation
Applications built on this gem are expected to trust `WebhookMetadata#shop` (and `Request#shop`) as an authenticated tenant identifier once `Utils::HmacValidator.validate` passes — that is the entire point of verifying the HMAC before dispatch. Because the shop header sits outside the signed bytes, an attacker can decouple "whose secret signed this payload" from "which shop this event is attributed to." Depending on how the host app persists or acts on webhook data keyed by `shop`, this allows cross-tenant data confusion: order/customer/GDPR payloads legitimately signed for the attacker's own shop can be attributed to a victim shop, or vice versa, without possessing the victim's credentials. This matches the Critical "cross-tenant access" category since it lets an unprivileged actor make the app process events under an arbitrary tenant identity.

### Likelihood Explanation
The only precondition is that the attacker obtains one valid `(body, hmac)` pair for the app's configured secret — trivially achievable by installing the app on the attacker's own store (a normal, unprivileged action) and capturing any webhook Shopify sends. From there, replaying the body with a different `shopify-shop-domain` header to the app's public webhook endpoint requires nothing more than an HTTP client. The gem performs no check that the header-derived `shop` matches any value bound into the HMAC.

### Recommendation
Bind the shop (and ideally topic/api-version/webhook-id) into the signed material, or independently verify that `request.shop` corresponds to a shop that actually has this app installed (e.g., cross-check against a known/installed-shops store) before invoking the handler in `Registry.process`. At minimum, document/enforce that consuming apps must not treat `WebhookMetadata#shop` as authenticated unless they perform this additional check themselves.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; capture a legitimate webhook delivery's raw body and its `X-Shopify-Hmac-Sha256` header (both signed correctly by Shopify with the app's real secret).
2. Send a POST to the app's webhook endpoint with the identical raw body and HMAC header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.to_signable_string` (the raw body) against the secret — see `lib/shopify_api/utils/hmac_validator.rb` lines 26-31.
4. The handler receives `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` — see `lib/shopify_api/webhooks/registry.rb` lines 198-199 — even though the payload was never signed in relation to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
