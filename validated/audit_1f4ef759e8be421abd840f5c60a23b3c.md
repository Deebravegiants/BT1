### Title
Webhook `shop` field is trusted for tenant attribution but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `hmac` and `to_signable_string` used for signature verification purely from the raw request body, while the `shop` (tenant identity) is read from an unauthenticated HTTP header. `Registry.process` validates only the body HMAC and then forwards the header-derived `shop` value to the app's `WebhookHandler` unchanged, so the tenant-attribution field is not bound by the same signature that authenticates the request.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string`. For webhook requests this is simply the raw body: [1](#0-0) 

The `shop` accessor used for tenant attribution is instead pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` checks only `Utils::HmacValidator.validate(request)` (i.e., the body signature) and then hands `request.shop` straight through to the app-supplied handler as part of `WebhookMetadata`: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `hmac(secret, signed_bytes) == received_hmac` implies `shop == the shop that produced signed_bytes`. In this implementation that equality does not hold, because `signed_bytes` (the raw body) contains no reference to `shop` at all — `shop` is carried entirely out-of-band in a header that anyone forwarding, replaying, or proxying the request can rewrite without invalidating the HMAC.

### Impact Explanation
Any party capable of receiving one genuine, correctly-signed webhook for their own shop (which is the normal, unprivileged flow for any merchant that installs the app) possesses a `(body, hmac)` pair that remains valid under `HmacValidator.validate` no matter what `shop-domain` header value is later attached to it. If that request is retransmitted to the app's webhook endpoint with the `shop-domain` header changed to a different, victim tenant, `Registry.process` still succeeds (body HMAC still checks out) and the app's handler receives `WebhookMetadata` claiming the payload originated from the victim shop. Any app logic that keys per-tenant state changes off `data.shop` (uninstall handling, redaction, order/customer processing, entitlement changes, etc.) can be manipulated to act against the wrong tenant using data the attacker legitimately possesses about their own store. This is a cross-tenant identity confusion that requires no access to the app's `client_secret`.

### Likelihood Explanation
Likelihood is high for any app that only relies on this gem's built-in `HmacValidator.validate`/`Registry.process` path (which is the documented mechanism) without independently re-verifying `shop` against an out-of-band trusted source (e.g., cross-checking against a list of shops that have valid stored sessions). No secrets are needed by the attacker beyond a webhook they legitimately received for their own shop; only header manipulation on replay is required, which is a capability any client or proxy sending the HTTP request has.

### Recommendation
Bind the tenant identity into the signed material or otherwise attribute the webhook payload only from the body, not the header. Concretely:
- Include the shop domain in `to_signable_string` (if Shopify's real signing scheme allows binding it), or
- After HMAC validation, cross-check `request.shop` against known/expected shop identifiers (e.g., only accept shops that the app has an active session/subscription for) instead of unconditionally trusting the header for routing, and
- Document explicitly in `docs/usage/webhooks.md` that `shop` from `WebhookMetadata` is not covered by the HMAC and must be independently validated by the host application before use in any privileged/tenant-scoped operation.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's secret), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same `B`/`H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this still passes. [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...)`, causing the app to process attacker-controlled data as if it came from `victim.myshopify.com`. [6](#0-5)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
