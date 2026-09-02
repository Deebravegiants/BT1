### Title
Webhook `shop-domain` header is not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only. The `shop-domain` header — the value the gem passes to the app's handler as the authoritative tenant identifier — is never included in the signed bytes. This breaks the binding: `HMAC-authenticated bytes == bytes the app trusts for shop identity`. An attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's shared secret (e.g. from a webhook delivered to their own, attacker-owned shop/install) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header, and `HmacValidator.validate` will still return `true`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the body or HMAC: [2](#0-1) 

`HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e. the raw body) against the shared `api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity dispatched to the app's handler, without any additional check that the shop actually matches the signed payload: [4](#0-3) 

That `shop` value flows unmodified into `WebhookMetadata`, which is the struct app code uses as the tenant key when processing the payload: [5](#0-4) 

Because the app secret (`api_secret_key`) is shared across every shop that installs the app, the HMAC over a given `raw_body` is identical regardless of which shop it originated from. Consequently:
- equality that should hold: `hmac == HMAC(secret, raw_body || shop)` (shop bound into the signed material)
- equality that actually holds: `hmac == HMAC(secret, raw_body)` (shop excluded)

An attacker who is themselves a merchant/installer of the target app (an "unprivileged internet user" with respect to any other tenant) receives their own genuine, Shopify-signed webhooks. They can capture any `(raw_body, hmac)` pair from a webhook delivered to their own store — or, for topics with predictable/attacker-influenced bodies (e.g. an empty-body-equivalent event, or a payload whose JSON they control the content of within their own shop) — and replay that exact body and HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to the victim shop's domain. `HmacValidator.validate` re-computes the same HMAC over the same `raw_body` and returns `true`, so `Registry.process` accepts the forged request and calls the app's handler with `WebhookMetadata.shop` set to the victim's domain.

### Impact Explanation
This crosses a tenant boundary using only content the attacker legitimately controls (their own account's webhook deliveries), satisfying the "cross-tenant access" high/critical bar. Any application logic that trusts `data.shop` from `WebhookMetadata` to select which merchant's records to create, update, or delete (the exact intended usage pattern documented for this gem) can be tricked into attributing attacker-supplied webhook data to a victim shop, or into triggering shop-scoped side effects (e.g. re-triggering install/uninstall handling, order-processing side effects, data sync) under an incorrect tenant identity — without needing the victim's access token, TLS interception, or any privileged credential. The root cause is entirely within this gem: the `VerifiableQuery`/`HmacValidator` contract signs the wrong scope of data for `Webhooks::Request`.

### Likelihood Explanation
Requires only: (1) the attacker to be an installer of the same app (i.e. possess a legitimate account with the target app, which is the normal, unprivileged position of any merchant), (2) network access to the app's public webhook endpoint, and (3) the ability to obtain at least one genuine `(body, hmac)` pair — trivially available since Shopify delivers signed webhooks to every installed shop, including the attacker's own. No secret material, session, or victim interaction is needed. Likelihood is Medium-High for apps whose webhook handlers act on `WebhookMetadata.shop` (the documented/intended usage), though exploitability for a specific victim depends on whether webhook payload content can be made attacker-influenced or coincide across shops (some topics/bodies are more attacker-controllable than others).

### Recommendation
Bind the shop identity into the signed material verified for webhook requests, or otherwise cross-check it out-of-band:
- Prefer verifying against Shopify's documented behavior: the HMAC is only ever valid proof that the body came from Shopify for *this app*, not for a specific shop — so `Registry.process`/the gem's documentation should explicitly warn/require that consuming apps additionally verify `request.shop` is a shop actually installed for/associated with this app instance before trusting it, or
- If feasible, include the shop domain in the signable string used for webhook HMAC validation (matching how `AuthQuery`/`VerifiableQuery` bind multiple fields for OAuth), so a forged `shop-domain` header invalidates the signature.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a genuine Shopify webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a POST to the app's webhook endpoint with:
   - body: `B` (unchanged)
   - header `x-shopify-hmac-sha256: H` (unchanged)
   - header `x-shopify-shop-domain: victim.myshopify.com` (forged)
   - header `x-shopify-topic`: same or different topic value, as needed
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`:
   - `Utils::HmacValidator.validate(request)` recomputes `HMAC-SHA256(api_secret_key, B)`, which equals `H`, so validation passes. [6](#0-5) 
   - The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed B, ...)`, i.e. the app processes attacker-supplied content as if it belongs to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
