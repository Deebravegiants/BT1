### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing in `Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the `shop` value that is later trusted and forwarded to the handler is taken from an unauthenticated HTTP header. This breaks the identity binding `shop authenticated == shop acted on`, matching the report's bug class of "a field acted on but not covered by the HMAC."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header with no relation to the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC over `to_signable_string` (the body), and, once that check passes, unconditionally trusts `request.shop` and hands it to the registered handler as the tenant identity for the event: [3](#0-2) 

`HmacValidator.validate` confirms the check is exactly `hmac(body, secret) == received_hmac`, with no reference to headers at all: [4](#0-3) 

Because the app's `api_secret_key` is shared across all shops that install the app (this is not a per-shop secret — see the OAuth callback HMAC using the same `Context.api_secret_key`), an unprivileged actor who is simply a merchant with the app installed on their own shop can:
1. Trigger any webhook event on their own shop and capture the resulting `raw_body` + valid `x-shopify-hmac-sha256` value (a completely legitimate signed message for their own tenant).
2. Replay that exact `raw_body`/HMAC pair to the app's webhook endpoint, substituting the `x-shopify-shop-domain` header with a different, victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks `raw_body` against the HMAC — the substituted `shop-domain` header is never covered by the signature.
4. `Registry.process` then calls the handler with `WebhookMetadata.new(topic:, shop: <attacker-chosen victim shop>, body:, ...)`, so the host application processes attacker-supplied body content as if it originated from the victim tenant.

This is the exact "shop authenticated versus shop acted on" binding break called out in scope: before the request, `hmac_valid(body) == true` binds only to the body; after the request, the application acts on `shop = header value`, which is a completely different, unauthenticated quantity.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` from `ShopifyAPI::Webhooks::Registry.process` to select which merchant's tenant data to create/update/delete (the documented and expected usage pattern, since `shop` is provided specifically for that purpose) can be made to write, mutate, or trigger business logic against a shop that never sent that data — a cross-tenant data-integrity/access violation. Depending on what the handler does with `body`/`shop` (e.g., updating order state, fulfillment records, billing, or entitlements keyed by shop), this can range from data corruption to logic bypass across tenants, which meets the "High: cross-tenant access" bar in scope.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker must control at least one shop with the target app installed (no leaked secrets, access tokens, or privileged accounts required — installing an app on your own store is the baseline unprivileged capability for any Shopify merchant/developer), and must be able to reach the app's public webhook endpoint directly with a forged header, bypassing Shopify's own webhook delivery infrastructure. Since this gem provides no additional binding of `shop` to the signed bytes and no default verification that the header shop matches an app-known/installed shop, nothing in the library itself prevents this replay.

### Recommendation
Include the shop-domain (and ideally webhook id / topic) in the HMAC-covered signable string, or otherwise cryptographically bind `shop` to the verified payload, e.g. by having `to_signable_string` concatenate the header value(s) with the body before computing/verifying the digest, and rejecting mismatches. Documentation for `Registry.process` should also explicitly warn implementers that `WebhookMetadata#shop` is not itself authenticated by the HMAC and must be cross-checked against known installed shops before being trusted for tenant-scoped operations.

### Proof of Concept
1. As the attacker, install the target app on `attacker-shop.myshopify.com` (fully legitimate, unprivileged action).
2. Trigger a webhook event (e.g., `orders/create`) on `attacker-shop.myshopify.com`; capture the raw POST body and the `x-shopify-hmac-sha256` value Shopify sends.
3. Send a new HTTP POST directly to the target app's webhook endpoint with:
   - Body: the exact captured `raw_body`
   - Header `x-shopify-hmac-sha256`: the exact captured HMAC value
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com` (any shop, does not need to be attacker-controlled)
   - Header `x-shopify-topic`: same topic as captured
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body bytes: [5](#0-4) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's own order body, even though `victim-shop.myshopify.com` never sent this webhook.

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
