### Title
Webhook HMAC signature does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` are taken directly from unauthenticated HTTP headers. This is the same bug class as the GMX report's core issue — a value that is *acted on* by downstream logic is not the same value that was *covered by the cryptographic check* — here applied to the identity-binding boundary between the verified payload and the claimed tenant (`shop`).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers, none of which participate in the signable string: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., only the body) and compares against `verifiable_query.hmac` (the `hmac-sha256` header): [3](#0-2) 

Once that body-only check passes, `Registry.process` immediately trusts `request.shop` as the tenant identity and forwards it to the app's handler: [4](#0-3) 

The equality the code implicitly assumes is:
`HMAC-verified(raw_body) == HMAC-verified(shop-domain header)`

but the actual guarantee provided is only:
`HMAC-verified(raw_body)` — the `shop-domain`, `topic`, and `webhook-id` headers are never bound to that signature.

Critically, the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is identical for every shop that installs the app — it is not shop-specific. This means any shop that has installed the app can obtain a completely valid `(body, hmac)` pair from Shopify (for its own legitimate webhook deliveries), then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds (it never looked at the shop header), and `WebhookMetadata` is built using the attacker-supplied `shop` value, per `docs/usage/webhooks.md` line 26 sample (`shop_domain: data.shop`).

### Impact Explanation
This breaks the shop/tenant identity binding relied on by any app built on this gem: an app that uses `data.shop` from `WebhookMetadata` to select which merchant record/session/access token to act on (the documented and expected usage pattern) can be made to process an attacker-chosen body under a victim shop's identity — a cross-tenant confusion/access issue. Any merchant that installs the app (an ordinary, unprivileged action available to any internet user who creates a Shopify dev/partner store) can harvest valid `(body, hmac)` pairs and use them to inject webhook events attributed to a different shop.

### Likelihood Explanation
The webhook endpoint is a public HTTP endpoint by design (`docs/usage/webhooks.md` lines 125-136), and becoming a "shop" that receives legitimately signed webhooks requires no privileged access — just installing the app on any store, which is the definition of an unprivileged internet user in this context. No leaked secrets, TLS interception, or social engineering is required; only observation/capture of the app's own outgoing webhook traffic delivered to the attacker's own shop.

### Recommendation
Include the identity-relevant header values (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable string, or otherwise cryptographically bind them to the payload verification (e.g., have `HmacValidator` also validate an out-of-band signature covering headers), so that a validated request cannot be replayed with a substituted shop identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker's app endpoint receives a legitimate webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the identical `(B, H)` pair to the same endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com"...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(api_secret_key, B) == H` — this passes.
5. `Registry.process` invokes the app handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, per [5](#0-4) , causing the app to act as if the event originated from the victim shop.

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
