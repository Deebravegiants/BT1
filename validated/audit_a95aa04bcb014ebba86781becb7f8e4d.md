### Title
Webhook `shop` Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
This is the same bug class as the Convex `fastCollateralCheck()` finding: a value that is *acted on* by security-sensitive logic is not the same value that was *verified*. In the Convex case, the balance checked was not the balance passed to the collateral check. Here, the `shop` identity attributed to an incoming webhook is not covered by the HMAC signature that is actually verified, breaking the binding `verified_bytes == attributed_tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives its `hmac` and `to_signable_string` exclusively from the raw request body: [1](#0-0) 

Note that `to_signable_string` returns only `@raw_body` — the `shop` (from the `shopify-shop-domain` / `x-shopify-shop-domain` header) is never included in the signed content: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — recomputes the HMAC over `verifiable_query.to_signable_string` (the raw body only) and compares it to the received HMAC: [3](#0-2) [4](#0-3) 

After this single check succeeds, `request.shop` (the unauthenticated header value) is passed straight into `WebhookMetadata` and handed to the host application's handler as the tenant identifier for the event: [5](#0-4) 

The equality the code should be enforcing is:
`hmac_verified(shop || body) == shop_used_for_tenant_attribution`

What it actually enforces is:
`hmac_verified(body) ; shop_used_for_tenant_attribution = header (unverified)`

Because the shop header sits completely outside the signed content, any request whose *body* carries a valid signature (the attacker need only have access to one legitimately-signed body+HMAC pair for their own shop) can be re-submitted with an arbitrary `shopify-shop-domain` header value, and it will pass HMAC validation and be routed to the handler under the attacker-chosen shop identity.

### Impact Explanation
This breaks the shop/tenant identity binding rather than a token-balance binding: `Registry.process` will faithfully report `HmacValidator.validate(request)` as `true` and dispatch `WebhookMetadata` claiming an arbitrary `shop` value that was never authenticated. A host application that persists or acts on webhook data keyed by `WebhookMetadata#shop` (this is the gem's own documented usage pattern, since `shop` is explicitly surfaced as a first-class field of the metadata struct) can be made to apply another merchant's/attacker-controlled body content under a victim shop's identity — i.e., cross-tenant data injection/confusion, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs the ability to send an HTTP request to the app's webhook endpoint with a body+HMAC pair that is valid for *some* shop (trivially obtainable by owning any shop that installs the same app and receiving one legitimate webhook), then replay it with a modified `shop` header. No access to `api_secret_key`, access tokens, or privileged accounts is required — this is reachable by an ordinary unprivileged merchant/internet user interacting with the public webhook endpoint the app exposes, which is exactly the kind of boundary this analog targets.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) header values into the signed content that `HmacValidator` verifies, or otherwise require the caller to independently authenticate the shop domain (e.g., verify it matches an existing app installation record) before trusting `WebhookMetadata#shop`. At minimum, the gem should document/enforce that `shop` cannot be treated as authenticated purely because `HmacValidator.validate` returned `true`.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the identical `B`/`H` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Webhooks::Request.new(raw_body: B, headers: {...shop: "victim.myshopify.com", hmac: H})` is constructed; `to_signable_string` returns `B`, so `Utils::HmacValidator.validate(request)` returns `true` (per `hmac_validator.rb` lines 26-31 and `request.rb` lines 10-13/35-38).
4. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)` to the app's handler, which believes this event genuinely originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
