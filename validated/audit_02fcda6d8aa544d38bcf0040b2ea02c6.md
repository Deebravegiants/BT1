### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable payload from the raw body only, while the `shop` (tenant) attribute is read from an unauthenticated HTTP header. Any party holding one *valid* signed webhook payload (e.g., from a shop where the app is installed, since the signing `api_secret_key` is shared across all shops for a given app) can replay that exact body while substituting the `shopify-shop-domain` header for a different victim shop. `ShopifyAPI::Webhooks::Registry.process` verifies only the HMAC of the body and then forwards `request.shop` — unauthenticated — to the app's handler, causing the webhook to be attributed to the wrong tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is derived purely from an HTTP header that is not part of the signed material: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e. the body) and then hands `request.shop` directly to the registered handler as trusted tenant identity: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever compares the computed HMAC of `verifiable_query.to_signable_string` (the body) against the received HMAC — it never binds the `shop` header into the digest: [4](#0-3) 

This breaks the intended identity binding:
`HMAC(body, api_secret_key) == received_hmac` should imply `shop header == shop that produced this body`, but the equality actually verified is only `HMAC(body) == received_hmac`, with `shop` free to be substituted by anyone able to produce (or replay) a validly-signed body for the same app.

### Impact Explanation
Because the `api_secret_key` is shared by the app across every shop where it is installed, any tenant that has the app installed can capture one legitimately-signed webhook body it receives (the signature only covers the body) and replay that exact body with the `x-shopify-shop-domain`/`shopify-shop-domain` header changed to point at a different, victim shop. `Registry.process` will accept the HMAC (it's valid for that body) and dispatch `WebhookMetadata.new(topic:, shop: request.shop, body:, api_version:, webhook_id:)` to the app's business logic under the victim's tenant identity. Any app logic keyed on `shop` (e.g., creating orders/fulfillments, updating billing state, writing per-shop DB rows) executes as if the data belongs to the victim shop — a cross-tenant data/identity confusion driven entirely by an unauthenticated header field.

### Likelihood Explanation
Any developer/merchant who can install the target app on their own shop (a normal, unprivileged action) automatically receives real webhooks with valid signatures for arbitrary bodies they can influence (e.g., by creating orders, products, etc. in their own store) and can immediately replay them against the same public webhook endpoint with a forged `shop-domain` header — no access to `api_secret_key`, access tokens, or TLS interception required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`/`api_version`) header values into the signable string used for HMAC verification, or otherwise cross-check the header-derived `shop` against a value that is itself covered by the signature, so that tampering with the shop header invalidates the HMAC. At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop-domain header (and other identity-bearing headers) rather than the body alone.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (app's `api_secret_key` is shared across all installs).
2. Attacker triggers a webhook (e.g. `orders/create`) and captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(B, api_secret_key)` as validated by `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb`.
3. Attacker resends the exact same request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `shop` returns `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/request.rb:20-23`), while `hmac` still validates successfully because `to_signable_string` never included the shop header (`lib/shopify_api/webhooks/request.rb:35-38`).
5. `ShopifyAPI::Webhooks::Registry.process` accepts the request (`Utils::HmacValidator.validate(request)` passes) and invokes the app's handler with `WebhookMetadata` reporting `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled data as if it originated from the victim tenant.

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
