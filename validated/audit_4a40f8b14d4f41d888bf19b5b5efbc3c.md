### Title
Webhook shop-domain not covered by HMAC, allowing cross-tenant shop spoofing via header manipulation - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC over the raw request body, then trusts the `shopify-shop-domain` (or `x-shopify-shop-domain`) header — which is completely outside the HMAC's coverage — as the tenant identity passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
`to_signable_string` returns only `@raw_body`. The `shop` accessor, however, is read straight from an attacker-controllable header with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, and then forwards `request.shop` (the unauthenticated header) directly to the handler as the tenant identity for the webhook: [3](#0-2) 

The identity binding that should hold is: `shop_header == shop_bound_by_hmac`. In reality, the HMAC only binds `raw_body`, so `shop_header` can be freely substituted by anyone who possesses one valid `(raw_body, hmac)` pair for the app's shared `api_secret_key` — e.g., an attacker who legitimately installed the app on their own (attacker-controlled) shop and thus legitimately receives correctly-signed webhook deliveries for that shop. They can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed, because `compute_signature(verifiable_query.to_signable_string, secret)` only depends on `raw_body`: [4](#0-3) 

The `shop` field is never checked against anything cryptographically tied to the body (there is no re-validation via `ShopValidator` or comparison to an installed-shop list inside this gem), so `WebhookMetadata`/handler code that keys off `data.shop` (as demonstrated in the registry's own tests) receives an attacker-chosen tenant identifier alongside a genuinely-signed-but-foreign payload.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce for webhook delivery: an app built on this gem that uses `request.shop`/`WebhookMetadata#shop` to select or scope per-shop state (e.g., look up the shop's stored access token/session, or attribute the webhook's contents to a shop record) can be tricked into processing a correctly-signed payload under a different tenant's identity — a cross-tenant identity confusion originating entirely from this gem's webhook verification contract (HMAC covers body only, but the gem hands back an unauthenticated `shop` value as if it were verified). This matches the Critical category of cross-tenant access via a field acted upon but excluded from the HMAC.

### Likelihood Explanation
Any unprivileged user can obtain a legitimately-signed `(body, hmac)` pair simply by installing the app (even a free/dev shop) and observing an inbound webhook, since the same `api_secret_key` signs every shop's webhooks for a given app. Forging the header afterward requires only crafting an HTTP request, no credentials beyond that.

### Recommendation
Bind the shop identity into the verified signable string (as is already done for `AuthQuery`, which includes `shop` in `to_signable_string`), or have `Registry.process` cross-check `request.shop` against a signed value / a known list of shops with active sessions before dispatching to handlers, so a replayed body cannot be attributed to an arbitrary shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the same request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `HMAC(secret, B)` — see [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)`, i.e., a genuinely-signed payload misattributed to a shop the attacker does not control.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
