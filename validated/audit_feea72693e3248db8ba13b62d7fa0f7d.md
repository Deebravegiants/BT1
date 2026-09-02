### Title
Webhook `shop` attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, and `ShopifyAPI::Webhooks::Registry.process` validates that signature and then trusts the unauthenticated `shop-domain` header to build the `WebhookMetadata` that host applications key their tenant-scoped logic on. The identity binding `hmac_verified_over(body) == shop_used_for_handler_attribution` does not hold, because the header carrying the shop identity is excluded from the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed data: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers the body) and then forwards `request.shop` unchanged into `WebhookMetadata`, which is what host apps use to route/attribute the event to a tenant: [3](#0-2) 

Because the shared app `client_secret` (and hence the HMAC key) is the same across every shop that installs the app, any merchant who installs the app on their own store can generate genuine webhook deliveries with a valid HMAC for a body of their choosing (e.g., by creating orders/products in their own shop to trigger `orders/create`, etc.). The HMAC signature that `Registry.process` validates says nothing about which shop the event belongs to — it only proves the body wasn't tampered with. An attacker who intercepts or replays such a delivery to the app's webhook endpoint can freely alter the `shop-domain` header to any other shop and the signature will still validate, since the header is outside `to_signable_string`.

This is structurally the same class of bug as the report's root cause: an attacker-controllable field (here, shop attribution) that is *acted on* by the consuming logic but *not covered* by the cryptographic check that is supposed to bind the identity of the actor to the operation.

### Impact Explanation
A successful forgery lets an attacker cause the host application's webhook handler to process attacker-supplied data while believing it originates from a victim shop (`WebhookMetadata#shop`). Depending on how the host app uses this metadata (e.g., to look up/update per-tenant records, cache invalidation, billing events, GDPR data requests), this is a cross-tenant data integrity issue: the app can be tricked into associating arbitrary attacker-chosen payloads with another merchant's tenant record.

### Likelihood Explanation
Likelihood requires only an attacker who has installed the app on any shop (an ordinary Shopify merchant, not a privileged actor) and the ability to intercept/replay the outbound webhook POST to the app's public endpoint (webhooks are delivered over plain HTTP(S) to the app-supplied callback URL, no additional secret required to modify in-flight headers if the attacker controls the network path or a proxy in front of their own endpoint testing setup, or via any MITM-capable position on that leg). No access to `api_secret_key`, tokens, or the target shop is required.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the signed payload verification, or independently verify that the `shop-domain` header corresponds to a shop actually known/installed for this app (cross-checked against stored session data) before trusting `WebhookMetadata#shop` in `Registry.process`. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically bound to the HMAC and must be revalidated by the host app against its own installed-shop list before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (normal merchant onboarding, no special privilege).
2. Attacker triggers a webhook event on their own shop (e.g. creates an order), causing Shopify to POST a body `B` with header `X-Shopify-Shop-Domain: attacker.myshopify.com` and a valid `X-Shopify-Hmac-Sha256: HMAC(client_secret, B)`.
3. Attacker intercepts/replays this request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` still succeeds because it only checks `HMAC(client_secret, B) == received_hmac`, per [4](#0-3) .
5. `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed_body(B), ...)`, causing the host app to process attacker-controlled data under the victim's tenant identity.

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
