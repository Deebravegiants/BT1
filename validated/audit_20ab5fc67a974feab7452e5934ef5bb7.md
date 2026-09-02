### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC only over the raw request body, while the `shop` (tenant) identity is taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed bytes. `ShopifyAPI::Webhooks::Registry.process` then dispatches the handler using this unauthenticated `shop` value as the trusted tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Request#shop` is read straight from the `shopify-shop-domain` header without any cryptographic binding to the body: [2](#0-1) .

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string` (i.e., the body) and the app's `api_secret_key`; it never inspects or binds the `shop` field: [3](#0-2) .

`Registry.process` validates only this body HMAC, then forwards the caller-controlled `request.shop` straight into `WebhookMetadata` as the authenticated tenant identity handed to the app's business logic: [4](#0-3) .

Since a single `api_secret_key` is shared by the app across *all* shops that installed it, any shop that has installed the app can obtain a genuinely-signed `(raw_body, hmac)` pair from its own legitimate webhook deliveries. The identity equality the code relies on is:
`shop_used_by_handler == shop_that_the_hmac_actually_authenticates`
This is false here — the HMAC authenticates only the body bytes, not the `shop` field, so `shop_used_by_handler` can be freely substituted by an attacker while `shop_that_the_hmac_actually_authenticates` (i.e., nothing about shop) stays valid.

### Impact Explanation
An unprivileged party who runs their own shop with the target app installed can capture one of their own legitimate webhook deliveries (valid body + valid HMAC, since it's genuinely signed by Shopify with the app's secret) and replay it to the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to point at a victim shop. `Registry.process` will accept it (HMAC validates fine, since it only checks the body) and dispatch the handler with `data.shop` set to the victim's domain. Any app logic keyed on `data.shop` for tenant attribution (e.g. "update this record for shop X", "look up this merchant's settings") is fed attacker-chosen tenant identity, producing cross-tenant data confusion/access — this maps to the Critical "cross-tenant access" category.

### Likelihood Explanation
Requires only that the attacker controls a shop where the app is installed (unprivileged, standard merchant access) and can capture/replay one of the app's own webhook calls, both trivially available to any installer of the app. No access token, `client_secret`, or privileged account is required.

### Recommendation
Bind the `shop` (and other identity-bearing headers, such as `topic`/`api_version`) into the signed payload verification, or independently verify that `request.shop` corresponds to a shop with an active, known session/installation before trusting it in `Registry.process`. At minimum, apps consuming `WebhookMetadata#shop` should be documented as needing to cross-check it against their own stored list of installed shops rather than trusting it implicitly — but ideally the gem itself should not hand off an unauthenticated field as if it were verified.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and the genuine `x-shopify-hmac-sha256` header Shopify sends (signed with the app's shared `api_secret_key`).
2. Attacker resends this exact `(raw_body, hmac)` pair to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` returns `true` because it only checks the body against the HMAC [5](#0-4) .
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker's own order data>, ...)` [6](#0-5) , causing the app to act on behalf of the victim shop using attacker-supplied data.

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

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
