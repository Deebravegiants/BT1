## Finding

### Title
Webhook `shop` identity is read from an unauthenticated header while HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read straight from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Registry#process` verifies only covers the raw request body (`to_signable_string` returns `@raw_body`). The `shop` value is never part of the signed bytes, so it is trusted without being cryptographically bound to the payload that was actually signed by Shopify.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are pulled from headers instead: [2](#0-1) 

`Registry#process` validates the HMAC over that signable string (the body only) and then immediately builds `WebhookMetadata` using `request.shop`, treating it as the authenticated tenant identity for the webhook: [3](#0-2) 

`HmacValidator.validate` confirms the signature is computed only from `to_signable_string`, i.e. the raw body bytes, never the headers: [4](#0-3) 

The identity binding that should hold is: `shop (used by handler) == shop (bound by the HMAC-signed bytes)`. In this implementation that equality never actually holds — the HMAC only proves "these body bytes were signed by Shopify with the app's secret", not "this body was signed for shop X". Any two webhooks that carry byte-identical bodies but originate from different shops (or a reused/replayed body) will produce the same valid HMAC, yet `request.shop` can be swapped independently since it comes from an unsigned header.

This is directly analogous to the veAERO report's root cause: an object (the (m)veAERO NFT / borrow-offer) is trusted as if the "locked value" and "collateral identity" were bound together, but the underlying mechanism (`Voter.withdrawManaged`) lets one side change independently of the other, breaking the assumed equality. Here, the assumed equality "signed body ⇔ shop" is broken because `shop` is carried by a header that sits entirely outside of the HMAC's signed scope.

### Impact Explanation
An attacker who controls a legitimate Shopify shop (any unprivileged merchant/developer account) receives genuinely Shopify-signed webhooks for their own shop. Because the `shop-domain` header is not part of the signed bytes, the attacker can replay the exact same raw body (and thus the exact same valid HMAC) to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry#process` will hand the host application a `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop. Any host app that trusts `request.shop`/`WebhookMetadata#shop` to select the tenant/session/database record to update is now processing attacker-controlled data under a victim tenant's identity — a cross-tenant data-integrity break reachable without any credentials beyond running one's own Shopify store.

### Likelihood Explanation
Requires only an unprivileged Shopify developer/merchant account to obtain one genuinely signed webhook body, and then requires the host application to route/act on `request.shop` (a very common pattern, since the library's own `Webhooks::Registry` API exposes `shop` in `WebhookMetadata` specifically for that purpose). No access to `api_secret_key` or any privileged credential is needed by the attacker — the gem's own signature-validation code path (`HmacValidator.validate` / `Request#to_signable_string`) is what fails to bind `shop` to the signed content.

### Recommendation
Include the shop-domain (and topic/webhook-id) header values in the HMAC-signable content, or otherwise independently verify that the `shop-domain` header matches an expected/registered shop for the given HMAC-validated body before exposing it via `Request#shop`/`WebhookMetadata`.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` receives a legitimate Shopify webhook: body `B`, headers include `X-Shopify-Hmac-Sha256: H` (valid for `B`), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the identical body `B` and identical `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry#process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and succeeds because `B` and `H` are unchanged.
4. `request.shop` now returns `victim.myshopify.com` (read from the forged header), and the handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` — attacker-controlled body data is now attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
