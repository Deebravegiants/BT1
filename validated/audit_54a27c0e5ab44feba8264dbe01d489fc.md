## Analysis

The webhook processing flow verifies request authenticity, but the HMAC signature only binds the raw request body — it does not bind the `shop` (or `topic`) that the gem trusts and forwards to the app's webhook handler. This is the exact bug class described in the report: a field (`shop`) is acted upon (used as the tenant identifier passed to the handler) without being covered by the cryptographic authentication check.

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read straight from an attacker-controllable HTTP header, independent of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` checks only that HMAC-over-body is valid, then immediately trusts `request.shop` as the tenant identity for the handler, with no cross-check that this shop is the one that produced the signature: [4](#0-3) 

Contrast this with the OAuth flow, where the equivalent identity fields (`shop`, `host`, `state`, `code`, `timestamp`) are all explicitly included in the signed string and thus bound to the HMAC: [5](#0-4) 

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw body. The `shop` value that the gem hands to application-supplied handlers as the trusted tenant identifier (`WebhookMetadata#shop`) comes from the `X-Shopify-Shop-Domain` header, which is completely outside the signed payload. Any party who can obtain one valid `(raw_body, hmac)` pair for their own installed shop — the only realistic actor here is an unprivileged internet user operating their own Shopify dev/trial store that has installed the app, so no Shopify secret key or victim credentials are required — can replay that exact body/HMAC pair to the app's webhook endpoint while swapping the `shop-domain` header to a victim shop. The `HmacValidator` will still pass (since it never looks at the shop header), and the handler will process attacker-supplied data under the victim's tenant identity.

### Finding Description
This mirrors the reported bug class precisely: the `stack` deletion targeted a copy (memory) instead of the authoritative storage, so the delete had no real effect where it mattered. Here, the equality that should hold is:

`shop value verified by HmacValidator == shop value delivered to the application handler`

But `HmacValidator.validate` only proves integrity of `@raw_body`; it says nothing about `shop`. `Registry.process` nonetheless forwards `request.shop` unchecked to `handler.handle`, so the binding is broken: HMAC-verified bytes (body) and the trusted-but-unverified bytes (shop header) diverge, exactly the "bytes verified versus bytes parsed" pattern called out as in-scope.

### Impact Explanation
Applications built on this gem are expected to key persisted webhook effects (order records, inventory writes, GDPR/customer data, uninstall handling, etc.) by `WebhookMetadata#shop`, since that's the only tenant identifier the gem exposes from a processed webhook. Because `shop` is unauthenticated, a malicious merchant who has legitimately installed the app on their own store can forge a webhook that the host application will process as belonging to a different shop, achieving cross-tenant data confusion/corruption purely through crafted HTTP requests to the app's public webhook endpoint. This satisfies the "cross-tenant access" Critical impact category, since it breaks the shop-to-request identity binding the gem is trusted to enforce.

### Likelihood Explanation
Likelihood is realistic: an attacker only needs (a) their own store where the app is installed, so Shopify will sign at least one webhook body with the shared secret, and (b) knowledge of the app's public webhook URL (typically not secret). No access token, no `client_secret`, and no victim credentials are needed — only replay of a header value.

### Recommendation
Bind the shop (and ideally topic) to the authenticated payload before trusting it, e.g. by including `shop-domain`/`topic` in the signable string alongside the body (matching how `AuthQuery#to_signable_string` binds `shop`/`host`/`state`), or by requiring the host application to independently confirm that the `shop` in a processed webhook belongs to a shop it expects to receive webhooks for (e.g. cross-checking against a known/installed-shop list) before trusting `WebhookMetadata#shop` for any state-changing operation. At minimum, document loudly that `request.shop` is not authenticated by `Registry.process` and must not be used as a sole tenant key.

### Proof of Concept
1. Attacker installs the target app on their own throwaway Shopify store, `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook: `raw_body = B`, `X-Shopify-Hmac-Sha256 = HMAC(secret, B)`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the same `raw_body = B` and the same valid `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only — it matches, so `Registry.process` proceeds.
5. The app's handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)` and performs whatever tenant-scoped action it normally performs on webhook receipt (e.g., updating victim's stored order/customer data) using attacker-controlled body content, without any actual signal that `victim.myshopify.com` sent anything.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
