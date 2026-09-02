### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body, while the shop identity used to dispatch the webhook to the host application (`request.shop`, taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header) is never included in the HMAC-covered content. This breaks the intended binding `HMAC-verified(raw_body) == trust-bound(shop)`: the signature authenticates the body bytes but not the tenant identity that the SDK hands to the application's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`request.shop` is read straight from an HTTP header that is not part of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC purely over `verifiable_query.to_signable_string` (i.e., the body), with no reference to any header field: [3](#0-2) 

`Registry.process` validates only that HMAC, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to construct `WebhookMetadata` passed to the app's handler — none of these header-derived values are cryptographically bound to the request: [4](#0-3) 

This is structurally the same defect class as the referenced report: a value that governs a security-relevant decision (`shop`, used for multi-tenant identity, analogous to `_effectiveDelegatedByHolderToValidator` governing bounty distribution) is left out of the mechanism (HMAC, analogous to the slash-reduction logic) that is supposed to keep it in sync/trustworthy. The signature check passes while the identity-bearing field it should be gating is silently unauthenticated.

### Impact Explanation
Any unprivileged actor who can obtain one authentic `(raw_body, hmac)` pair for a topic (e.g., by installing the target app on their own low-privilege development/trial shop and receiving a real webhook from Shopify) can replay that exact body and HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed because it only checks the body bytes, and `Registry.process` will hand the host application a `WebhookMetadata` claiming the body originates from the victim shop. If the host app uses `data.shop` (as the SDK's own docs/tests assume it will) to scope database writes, trigger shop-specific business logic, or look up which access token/session to act with, this results in cross-tenant data confusion/injection — data or events attributed to shop B are actually attacker-controlled content from shop A's webhook.

### Likelihood Explanation
Any developer/merchant can self-install an app that uses this gem and thereby legitimately harvest valid `(body, hmac)` pairs for arbitrary supported topics at will — no leaked secret, TLS interception, or privileged account required, satisfying the "unprivileged internet user" bar. The only remaining step is a plain HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header, which is fully within this gem's request-parsing contract (`Request#initialize` only requires the three headers to be present, never that they came from Shopify).

### Recommendation
Bind the tenant identity to the signature, e.g. include the `shop-domain` (and ideally `topic`/`webhook-id`) header value(s) in `to_signable_string` (as some HMAC schemes do), or otherwise verify `request.shop` via a channel that is itself authenticated (e.g., only trust `data.shop` when the app also has an independent verified session/token for that shop). Alternatively, document explicitly that host applications must not treat `shop-domain` as trustworthy without secondary verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers a webhook for topic `orders/create`.
2. Shopify sends a legitimate webhook: `raw_body = B`, headers include `x-shopify-hmac-sha256 = HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `B` and the valid HMAC, then sends a new POST to the same app endpoint with identical `raw_body = B` and identical HMAC header, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (per `lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `B` against the HMAC.
5. `Registry.process` (per `lib/shopify_api/webhooks/registry.rb:188-199`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches `B`'s content to the app's handler as though it were an authentic event for the victim shop.

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
