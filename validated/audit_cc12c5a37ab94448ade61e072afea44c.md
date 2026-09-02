### Title
Webhook `shop` (and `topic`) identity is taken from an unauthenticated HTTP header that is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by HMAC-validating only the raw request body, but then hands the handler a `shop` (and `topic`) value that is read from HTTP headers which are completely excluded from that signature. This breaks the binding "shop authenticated == shop the handler acts on," letting an attacker who owns one legitimate, HMAC-signed webhook body attribute that payload to a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC exclusively over that signable string (the body) and compares it against the `hmac-sha256` header: [2](#0-1) 

`Registry.process` calls this validator, and if it passes, immediately builds `WebhookMetadata` using `request.topic` and `request.shop`, both of which are read straight from headers (`shopify-shop-domain` / `x-shopify-shop-domain`, `shopify-topic` / `x-shopify-topic`) that are never included in the HMAC input: [3](#0-2) [4](#0-3) 

`WebhookMetadata.shop` is then passed straight to the host application's handler as the merchant identity for the event: [5](#0-4) 

Because every shop that installs a given app shares the same `api_secret_key`, any merchant who has installed the app can legitimately receive one authentic `(raw_body, hmac)` pair addressed to their own shop (e.g., a `customers/redact`, `shop/update`, or `app/uninstalled` webhook). That HMAC only certifies the body content — it says nothing about which shop the event belongs to. The attacker can then replay the exact same body and `hmac-sha256` header to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `HmacValidator.validate` will still succeed (the body/HMAC pair is untouched), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event is `for` the victim shop.

This is the same bug class as the `Cooler.claimDefaulted` finding: a value acted upon (`Cooler`'s lender identity / here, the webhook's `shop`) is not covered by the cryptographic check that is supposed to establish trust (the collateral/loan ownership check / here, the HMAC), letting an attacker splice a legitimately-signed artifact onto a different tenant's identity.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` to key data-deletion (GDPR `customers/redact`, `shop/redact`), access revocation (`app/uninstalled`), or other per-tenant side effects — which is the documented purpose of this field — an attacker can force those side effects to be applied to an arbitrary victim shop by replaying a self-obtained, validly-signed webhook body with a forged shop-domain header. This is a cross-tenant confusion/cross-tenant action vulnerability triggered entirely with data the attacker already legitimately possesses (their own webhook deliveries) and requires no access token, secret, or privileged account.

### Likelihood Explanation
Any merchant who installs the target app can obtain at least one legitimate `(body, hmac)` pair for their own shop (webhooks are delivered to a public HTTPS endpoint operated by the host app). Replaying that pair with a modified `Shop-Domain` header requires only basic HTTP tooling — no cryptographic secret, no TLS interception, and no elevated privileges. The main variable is whether/how strongly the host application uses `data.shop` for tenant-scoped actions, which is outside this gem, but the gem provides no protection and documents `shop` as a trustworthy field of `WebhookMetadata`.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the raw body before exposing them to handlers. At minimum, `HmacValidator`/`Request#to_signable_string` should incorporate the shop domain (and ideally topic) so a valid signature cannot be "moved" between shops, matching how `AuthQuery#to_signable_string` binds `shop` into the OAuth HMAC input.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook (e.g. `customers/redact`) to the app's public endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`, plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` (it was delivered to a URL/log they control, or they can trigger it themselves by performing the corresponding action, e.g. requesting their own data redaction).
4. Attacker sends a forged HTTP POST to the same app webhook endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H`. [6](#0-5) 
6. `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", ...)` is passed to the host app's handler, which now believes the event (e.g., a redact/uninstall action) legitimately originated from `victim.myshopify.com`. [7](#0-6)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
