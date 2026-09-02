### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (and `request.topic`) as the identity of the tenant the payload belongs to when building `WebhookMetadata` for the app's handler. However, the HMAC signature only covers the raw request body — it never covers the `shop`, `topic`, `webhook_id`, or `api_version` values, which are taken directly, unauthenticated, from HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator` computes/verifies the signature exclusively against `to_signable_string`: [2](#0-1) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from caller-supplied headers with no cryptographic binding to the body or the HMAC at all: [3](#0-2) 

`Registry.process` treats a passing `HmacValidator.validate` call as full authentication of the request, then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata`, which is handed to the app's business logic as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

Because a Shopify app's webhook secret (`api_secret_key`) is the **same for every shop that installs the app**, `HMAC(secret, raw_body)` is identical no matter which shop actually sent the payload. This is the direct analog of the reported bug class: a field ("shop") that is *acted on* (used to route/attribute the webhook to a tenant) is not *covered* by the authentication primitive (the HMAC), so the destination logic ends up validating the wrong binding — "HMAC-verified bytes" is checked, but the identity that's actually consumed ("attributed shop") is never checked at all.

Concretely, this breaks the equality that the documented API implies:
`shop_attributed_by_gem == shop_that_actually_produced_the_signed_body`

but the real binding enforced is only:
`HMAC(secret, raw_body) == received_hmac`

with `shop` free for an attacker to set independently.

### Impact Explanation
An unprivileged user who can install the target app on their own store (a normal, legitimate installation — no special privilege needed) will receive a batch of legitimately-signed `(raw_body, hmac)` pairs for their own shop's webhooks. Because the secret is shared across all shops of the app, that attacker can replay any of these bodies/HMACs verbatim to the app's public webhook endpoint while forging the `x-shopify-shop-domain` (and `x-shopify-topic`) header to name a **different, victim** shop. `HmacValidator.validate` still returns `true` (it only checks the body), so `Registry.process` proceeds and calls the host app's handler with `WebhookMetadata.shop` set to the victim shop even though the payload/body actually originated from the attacker's own shop. Any host app that follows this gem's documented pattern of trusting `WebhookMetadata.shop` post-HMAC-check (as shown in `docs/usage/webhooks.md`) will process attacker-controlled data under a different tenant's identity — i.e., cross-tenant data injection/confusion, which meets the Critical "cross-tenant access" bar since the trust boundary between tenants is bypassed using only the gem's own advertised authentication check.

### Likelihood Explanation
Any developer/merchant who can install the app (an unprivileged action available to any internet user for public apps) can obtain valid `(body, hmac)` pairs for their own tenant and replay them with a spoofed `shop-domain` header at will; no access token, `client_secret`, or leaked credential is required, only observation of the attacker's own legitimately-received webhook traffic.

### Recommendation
Bind the `shop` (and ideally `topic`) value into the signed material, or otherwise cryptographically verify it, before it is trusted as the tenant identifier. At minimum, `Utils::HmacValidator`/`Webhooks::Request#to_signable_string` should incorporate the `shop-domain` header into the HMAC-verified payload (matching how Shopify's own webhook signature scheme is documented to work per-topic/per-shop), or `Registry.process` should cross-check the header-derived `shop` against an independently trusted source (e.g., a lookup keyed by `webhook_id`/topic combination previously registered for that specific shop) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and captures a legitimate webhook delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body = B` and same HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `secret` (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing attacker-controlled data to be processed as if it belonged to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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
