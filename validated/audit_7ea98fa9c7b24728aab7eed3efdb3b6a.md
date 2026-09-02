### Title
Webhook `shop` identity claim is not covered by the HMAC signature, allowing tenant-spoofing via replayed webhook bodies - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` identity that is handed to the app's handler is read directly from the unauthenticated `x-shopify-shop-domain` header, which is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

and its `shop` accessor simply reads the `shop-domain` header, which is not part of that signed string: [2](#0-1) 

`Registry.process` validates only that HMAC: [3](#0-2) 

and then forwards `request.shop` (the unauthenticated header value) to the app's handler as the authoritative tenant identity via `WebhookMetadata`.

The identity binding that should hold is:
`shop_bytes_verified_by_hmac == shop_bytes_used_by_handler`

Here, the HMAC only covers `raw_body`; the `shop-domain` header used to build `WebhookMetadata#shop` is excluded from `to_signable_string`. Consequently:

`shop_bytes_verified_by_hmac` (nothing – body only) `!= shop_bytes_used_by_handler` (`x-shopify-shop-domain` header, attacker-controlled)

This mirrors the report's bug class exactly: a downstream action (`_processReferralRebate`/here, the handler's tenant-scoped logic) is invoked using a value (`isReferralValid`/here, `shop`) whose correctness is never actually checked by the guarding logic (`createFromRouter`/here, `HmacValidator.validate(request)`).

### Impact Explanation
Any unprivileged internet user who can obtain one valid `(raw_body, hmac)` pair — e.g. by installing the app on their own development/test store and capturing a genuine webhook delivery for that store — can replay that exact body and HMAC to the app's public webhook endpoint while setting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it only checks the body bytes against the secret, and `Registry.process` will invoke the registered handler with `WebhookMetadata#shop` set to the attacker's chosen shop domain. Any host application that uses this gem's documented `shop` field to load/mutate per-tenant records (a supported and expected usage of `WebhookMetadata`) can be tricked into acting on behalf of a shop the attacker does not own, i.e., cross-tenant access driven entirely through this gem's own trust decision.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and possession of one legitimately-signed webhook body (trivially obtainable by any merchant/developer who installs the app, even on a free/dev store, since the api_secret_key is shared across all shops using the app). No access token, TLS interception, or privileged account is required, and the technique does not rely on the host app ignoring documented API — it relies on this gem's `HmacValidator`/`Request` design not binding the `shop` claim into the signed payload.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signable content, or otherwise independently authenticate/pin the `shop-domain` header (e.g., compare it against an expected shop known from session/app-install context) before exposing it via `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays a POST to the app's webhook endpoint with the same body `B`, same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds ( [4](#0-3) ).
4. The registered handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` ( [5](#0-4) ), even though `victim-shop.myshopify.com` never sent this webhook and was never verified.

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
