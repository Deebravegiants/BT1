This confirms the vulnerability. The `Webhooks::Request.to_signable_string` (used by `Utils::HmacValidator.validate`) returns only `@raw_body` — the HMAC covers exclusively the body bytes, never the `shop-domain`, `topic`, or `webhook-id` headers. Yet `Registry.process` trusts `request.shop` directly to construct `WebhookMetadata` and dispatch it to the app's handler, without the shop being bound to the signature at all.

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0)  which is what `Utils::HmacValidator.validate` uses to recompute and compare the signature [2](#0-1) . The `shop` value dispatched to the app's webhook handler, however, is read straight from the `shopify-shop-domain` HTTP header without any cryptographic binding to that header [3](#0-2) . `Registry.process` validates only the HMAC over the body, then trusts `request.shop` to build the `WebhookMetadata` passed to the handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, bytes_that_include_the_tenant_identifier)`. In this gem it instead holds `hmac == HMAC(secret, raw_body_only)`, while `shop` (the tenant identifier acted upon by the handler) is taken from an unauthenticated header that is disjoint from the signed bytes.

Because Shopify webhook HMACs are signed with the **app-wide** `client_secret` (not a per-shop secret), any merchant who has installed the app can capture a legitimate webhook delivery to their own endpoint (body + `X-Shopify-Hmac-Sha256` value are both fully attacker-visible once received). That merchant, acting as an unprivileged internet user relative to other tenants of the same app, can then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never looks at that header [5](#0-4) , and `Registry.process` forwards the forged `shop` value straight to the handler [6](#0-5) .

Equality before/after the attack:
- Before: attacker legitimately owns webhook for `shop=attacker.myshopify.com`, `hmac = HMAC(secret, body)` — valid and correctly attributed.
- After: attacker resends identical `body`/`hmac`, but sets `shop-domain: victim.myshopify.com`. `hmac` still verifies (it never depended on the shop header), yet `WebhookMetadata.shop` now equals `victim.myshopify.com` — breaking the intended binding `verified_shop == header_shop`.

### Impact Explanation
Any app built on this gem that uses `data.shop` from `WebhookMetadata` to key persistence, trigger tenant-scoped side effects (e.g., processing `app/uninstalled`, `shop/redact`, `customers/redact`, inventory/order updates, billing state changes) will attribute a validly-signed-but-attacker-controlled payload to a different merchant's tenant. This is a cross-tenant access/data-confusion primitive: an attacker-controlled webhook body is accepted as authentic for a shop the attacker does not own, satisfying the "cross-tenant access" Critical impact category, since the shop identity is exactly the boundary meant to be enforced by webhook verification.

### Likelihood Explanation
Requires only that the attacker's own shop has the app installed (any merchant/free trial account qualifies as "unprivileged"), and the ability to send arbitrary HTTP requests to the app's public webhook endpoint — both trivially satisfied. No access token, `client_secret`, or privileged credential is needed.

### Recommendation
Include the tenant-identifying headers (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind the shop domain to the signature — e.g. by having `to_signable_string` incorporate the normalized shop header alongside the body, and rejecting mismatches. Shopify's actual webhook contract signs the raw body; a shim library like this should still be built so that consuming apps are not implicitly encouraged to trust an unauthenticated `shop` field returned by a "verified" webhook object. Document loudly that `request.shop` is not authenticated by `Utils::HmacValidator.validate`, or bind it into a value that is authenticated by the gem itself before exposing it on `WebhookMetadata`.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` has the target app installed; Shopify delivers a real webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (`H = HMAC-SHA256(client_secret, B)`), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays a POST to the same endpoint with identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. In the gem, `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `to_signable_string` returns `B` [1](#0-0) .
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(client_secret, B)`, matches `H`, returns `true` [5](#0-4) .
5. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)` [7](#0-6)  — the app now processes attacker-controlled data as if authentically originating for `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
