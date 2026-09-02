### Title
Webhook Shop Domain Header Not Covered by HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body, never the headers. An attacker who can obtain any one legitimately-signed webhook body/HMAC pair (e.g. by installing the target app on their own shop) can replay that exact body with a forged shop-domain header claiming to be a different, victim shop. The signature check still passes because it never inspects the header, so the host application's webhook handler processes attacker-controlled data under an arbitrary shop identity of the attacker's choosing.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop` (the tenant identity used downstream) is read directly from a header that is entirely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over that body-only signable string, and if it passes, immediately hands the *unauthenticated* `request.shop` value to the app's webhook handler as the tenant identity: [3](#0-2) 

The binding the gem is implicitly supposed to guarantee is:
`shop authenticated by HMAC == shop delivered to WebhookMetadata`

But in reality the equality is:
`shop covered by HMAC == ∅` (the shop header is never part of `to_signable_string`)
`shop delivered to WebhookMetadata == shop header value (attacker-controlled)`

This is exactly the "field acted on but not covered by the HMAC" bug class from the report: just as `IonZapper` acted on unapproved token transfers, this gem acts on an unauthenticated shop identity while believing the HMAC check has authenticated the whole request.

### Impact Explanation
Any consumer of this gem that uses `Webhooks::Registry.process` (the documented, intended usage per `docs/usage/webhooks.md`) and trusts `WebhookMetadata#shop` for tenant routing/authorization is exposed to cross-tenant data injection: an attacker can cause data intended to be scoped to shop A to be attributed to shop B merely by changing a header, without needing the app's `client_secret`. Depending on how the host app uses the shop field (e.g., to look up which merchant's records to update), this can lead to cross-tenant data corruption or unauthorized actions performed against a victim merchant's account — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The attacker only needs to be an unprivileged internet user who can install the target app on their own (attacker-controlled) shop — a normal, legitimate installation — to receive at least one genuinely Shopify-signed webhook body/HMAC pair for their own shop. They can then replay that exact body to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header changed to any victim shop domain. No secrets, tokens, or privileged access are required beyond normal app installation, so likelihood is high for any app relying on this gem's webhook processing.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` value to the signed body before it is trusted. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant routing without additional verification (e.g., cross-checking against a shop that is independently known to have a valid, subscribed webhook for that topic/id).

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev shop `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`). They capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends — both are valid because Shopify signed them with the app's real `client_secret`.
2. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets:
   `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the signature over `request.to_signable_string` (body only) — validation succeeds since the body/HMAC pair is genuinely valid, per [4](#0-3) .
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's order payload>, ...)`, as constructed at [5](#0-4) , causing the host app to process attacker-supplied data under the victim shop's identity.

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
