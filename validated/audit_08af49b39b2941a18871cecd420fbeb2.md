### Title
Webhook `shop` (and `topic`) identity is taken from unauthenticated HTTP headers not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the event to the registered handler using a `shop` value taken from an HTTP header that was never included in that signature. This breaks the intended binding `hmac == HMAC(secret, raw_body + shop + topic)` down to the weaker actual check `hmac == HMAC(secret, raw_body)`, letting an attacker who owns *any* valid `(raw_body, hmac)` pair replay it while forging the `shop` (and `topic`) the app believes the payload came from.

### Finding Description
The webhook request wraps the raw body and headers: [1](#0-0) [2](#0-1) 

`to_signable_string` — the value that `Utils::HmacValidator` actually verifies — is `@raw_body` only: [3](#0-2) 

Yet the dispatcher trusts `request.shop` and `request.topic`, both sourced from HTTP headers (`shopify-shop-domain`, `shopify-topic`) that are outside the signed material, to route and identify the tenant: [4](#0-3) 

The binding that should hold is: **the `shop` value acted upon by the handler == the `shop` value covered by the HMAC signature.** Before the fix this equality never has to hold — `Utils::HmacValidator.validate(request)` only checks `hmac == HMAC(secret, raw_body)` (headers excluded), while `handler.handle` is called with `shop: request.shop` read straight from the mutable header. This is the same class of bug as the reported issue: a field that participates in downstream trust decisions (`initialLongToken`/`initialShortToken` in the GMX report, `shop`/`topic` headers here) is not covered by the verification step that is supposed to authenticate the whole request (`executionFee` subtraction keyed off `market.longToken` instead of the actual transferred token there; `WebhookMetadata.shop` keyed off an unsigned header here).

### Impact Explanation
Any attacker capable of installing the target app on their own (attacker-controlled) development store will receive genuine webhook deliveries from Shopify — each carrying a body and an `X-Shopify-Hmac-SHA256` value computed with the app's real `api_secret_key`. Because the signature covers only the body, the attacker can resend that exact `(body, hmac)` pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) with a victim shop's domain / a different topic. `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: <victim shop>, topic: <forged topic>, body: <attacker's own data>, ...)`. Any app that uses `data.shop` to look up the tenant's session/DB record and persist or act on `data.body` (the documented, intended use of `WebhookHandler#handle`) will attribute the attacker's payload to the victim's tenant — a cross-tenant data-integrity/confusion primitive achieved without any of the excluded prerequisites (no access token, no leaked credentials, no TLS interception).

### Likelihood Explanation
Obtaining a valid `(raw_body, hmac)` pair requires no privilege beyond installing the app on any store, including a free attacker-owned development store, and observing one real webhook delivery. Replaying it with modified headers to the app's public webhook endpoint requires no authentication at all. The only defense in this gem is `Utils::HmacValidator.validate`, which — as shown — never inspects the `shop` or `topic` headers.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signed material that `Utils::HmacValidator` verifies, or independently bind `request.shop`/`request.topic` to values embedded in the signed body (Shopify webhook payloads typically contain enough context to cross-check). At minimum, `Registry.process` should refuse to trust `request.shop` unless it can be tied back to the HMAC-covered content, e.g. by having `Request#to_signable_string` incorporate the canonicalized header values that `WebhookMetadata` later relies on, mirroring the GMX fix of keying trust decisions off the value that's actually authenticated (`params.initialLongToken`) rather than an out-of-band value (`market.longToken`).

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled store `attacker-shop.myshopify.com`; trigger any webhook topic the app subscribes to (e.g. `products/create`) so Shopify delivers a POST with body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(secret, B)`.
2. Capture `B` and `H` from the attacker's own server logs.
3. Replay the exact same POST body `B` and header `H` to the app's public webhook endpoint, but replace:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - optionally `X-Shopify-Topic` with a different registered topic.
4. Server-side: `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which only recomputes `HMAC(secret, B)` and compares to `H` — this still matches. `Registry.process` then invokes `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: <forged>, body: JSON.parse(B), ...))`, causing the app to process the attacker's payload as if it originated from `victim-shop.myshopify.com`. [4](#0-3)  shows the exact dispatch path exploited above.

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
