### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that authenticates the webhook only covers the raw request body. This breaks the identity binding between "bytes verified" (the raw body) and "bytes acted on for tenant identity" (the shop header), allowing an attacker who legitimately owns one shop on a multi-tenant app to replay a genuine, HMAC-valid webhook body while substituting a different shop's domain in the header.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body` — no headers are part of the signed content. Meanwhile, `shop` (the field host applications use to identify which merchant/tenant the webhook belongs to) is pulled straight from an unauthenticated header: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC strictly against `to_signable_string`: [3](#0-2) 

Because the app's `api_secret_key` is shared across all shops that install the app (it is not per-tenant), any shop that legitimately installs the app can trigger a real webhook and thus obtain a body + valid HMAC pair signed with that shared secret. Nothing in the signed payload binds that HMAC to the specific `shop-domain` header value that arrived with it. A malicious app-installer can therefore capture their own valid `(raw_body, hmac)` pair and resend it to the webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop that also uses the same app. `Utils::HmacValidator.validate` will still return `true` because the signature check never examines the header, so `request.shop` — the value the host application uses to select which tenant's `Session`/access token/database row to operate on — is fully attacker-controlled while still passing signature validation.

This directly matches the allowed analog class: "a field acted on but not covered by the HMAC."

### Impact Explanation
If the host application uses `Webhooks::Request#shop` (as the library's own documented pattern encourages, since it's the only accessor for shop identity on this object) to select the tenant record to update/delete/react to (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`), an attacker who is any unprivileged merchant installer of the app can forge webhook events attributed to a different merchant, achieving cross-tenant access/manipulation without needing that victim's access token, session, or `client_secret`. This satisfies the Critical impact bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Requires only that the attacker install the app on their own store (an unprivileged action) to obtain one valid `(body, hmac)` pair signed under the shared app secret, then replay it with a modified `shop-domain` header — no credentials, tokens, or privileged access needed. This is directly reachable through the gem's own public webhook-verification API (`Webhooks::Request` + `Utils::HmacValidator.validate`), not a misuse of undocumented behavior.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header value into the signed content used for verification, or require host applications to cross-check `request.shop` against an independently-trusted, previously-registered shop record (keyed by something bound to the HMAC, such as a per-shop webhook secret or a shop verified via a prior OAuth/session-token flow) before trusting it for tenant selection. At minimum, the library should document prominently that `shop` is unauthenticated and must not be used alone to select tenant state.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged onboarding flow).
2. Shopify sends a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-SHA256: H`, where `H = HMAC_SHA256(secret, B)`.
3. Attacker resends the exact same body `B` and signature `H` to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H})` is constructed; `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` never includes the header.
5. The host application's webhook handler, trusting `request.shop`, applies the webhook's effect (e.g., session/data invalidation tied to `app/uninstalled`) to `victim-shop.myshopify.com` — a shop the attacker never controls.

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
