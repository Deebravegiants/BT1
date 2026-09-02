### Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Allowing Cross-Tenant Shop Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while `request.shop` (the tenant identifier passed to app handlers) is read from a separate, unsigned header. Anyone who possesses one valid `(raw_body, hmac)` pair — trivially obtainable by installing the app on their own store and capturing a webhook — can replay those exact bytes to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. `HmacValidator.validate` will still pass because it never inspects the shop header, and `Registry.process` will hand the forged shop identity to the app's handler as if it were authentic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header and is never mixed into the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC strictly against `to_signable_string` (i.e., the body only): [3](#0-2) 

`Registry.process` trusts the header-derived `request.shop` to build tenant context for the app's handler immediately after the (body-only) HMAC check succeeds: [4](#0-3) 

The identity binding that should hold is: `shop header used by handler == shop that the HMAC-signing secret was applied on behalf of`. Because the HMAC only covers `raw_body` and not the `shop` header, this equality is never enforced by the gem: `verified_bytes (raw_body) != bytes_that_determine_tenant (shop header)`. An attacker who is a genuine (even free/trial) merchant on their own store can receive a legitimate webhook (valid body + valid HMAC signed with the app's real `client_secret`), then POST the identical body and HMAC to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` recomputes HMAC over the same body and matches, so the forged request is accepted, and `Registry.process` invokes the handler with `shop: <victim shop>` even though the payload never originated from, nor was authorized for, that shop.

### Impact Explanation
This breaks the tenant-binding guarantee the gem is supposed to provide to consuming apps: the `shop` value handed to `WebhookMetadata`/handlers is the primary key many apps use to select which merchant's data/record to mutate. Because it is unauthenticated, an unprivileged internet user (any installer of the same app on any shop) can inject webhook events that are cryptographically valid yet falsely attributed to an arbitrary other shop, producing cross-tenant data confusion/corruption in any downstream application relying on `data.shop` from the gem's webhook processing pipeline — e.g., forged `app/uninstalled`, `shop/redact`, or business events processed for the wrong tenant. This matches the Critical "cross-tenant access" category, since the boundary broken is the identity binding between the signed bytes and the tenant field the app trusts.

### Likelihood Explanation
Likelihood is high for any deployment that exposes the standard webhook endpoint publicly (as is required for Shopify to deliver webhooks). The only prerequisite for an attacker is a single legitimate webhook capture for any shop (including their own store, freely installable), and standard tooling (curl) to replay it with a modified header — no access to `client_secret`, access tokens, or privileged accounts is required.

### Recommendation
Bind the shop identity cryptographically to the verified request instead of trusting an unsigned header:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) values in the HMAC-signed payload (`to_signable_string`) so any tampering invalidates the signature, or
- Cross-validate the header-derived `shop` against an independent trust anchor (e.g., confirm the shop has an active, matching offline session/access token before dispatching the handler), rejecting requests where the header shop cannot be corroborated.
- At minimum, document this trust boundary prominently and require consuming apps to independently verify `data.shop` against known installed shops before performing any tenant-scoped mutation.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives (or triggers) a webhook delivery, capturing the raw body `B` and the `x-shopify-hmac-sha256` header value `H` (computed by Shopify over `B` using the app's real `client_secret`).
2. Attacker sends a POST directly to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256`: `H` (unchanged)
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic`: unchanged or attacker-chosen registered topic
3. `ShopifyAPI::Webhooks::Request.new` parses these headers/body without issue.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and compares it to `H` — this succeeds because the signature never covered the shop header.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it came from `victim-shop.myshopify.com`.

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
