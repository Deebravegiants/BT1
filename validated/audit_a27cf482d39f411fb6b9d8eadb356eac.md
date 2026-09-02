Based on my investigation, I've confirmed the vulnerability. Here's the finding:

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (and `topic`, `api-version`, `webhook-id`) values come from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC against the body and then unconditionally forwards `request.shop` to the app's handler as the tenant identifier, without verifying that the header-derived shop is bound to the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, with no cryptographic binding to the signed body: [2](#0-1) 

`HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`, i.e., only the body is verified: [3](#0-2) 

`Registry.process` validates the HMAC and then passes the *unverified* `request.shop` straight to the app's webhook handler as the tenant identifier: [4](#0-3) 

This breaks the intended identity binding: `HMAC(raw_body, client_secret) == received_hmac` is verified, but the equality that actually matters for tenant isolation — `shop_header == shop_that_produced(raw_body)` — is never checked. Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's `client_secret` for *any* shop (trivially available to a developer/attacker who installs the app on their own store and receives a real webhook) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. The HMAC check still passes because it only covers `@raw_body`, and the registry forwards the forged shop value to the handler as if it were verified.

### Impact Explanation
This is a cross-tenant boundary break: an unprivileged attacker who legitimately controls one shop installation can cause the app to process fabricated events (e.g., `orders/create`, `app/uninstalled`, `customers/data_request`) as if they belong to a different merchant. Applications typically use `WebhookMetadata#shop` to look up the target merchant's stored session/access token and perform side effects (data writes, deletions, redaction, billing actions, sending the victim's stored access token in follow-up API calls) on behalf of that shop. Since the gem provides no guarantee that `shop` is authenticated, any host application that follows the documented contract (trusting the `shop` field on a "verified" webhook) is exposed to cross-tenant data manipulation.

### Likelihood Explanation
High likelihood: the only prerequisite is that the attacker has valid access to at least one legitimate webhook (their own store's, or one previously observed), since `client_secret` is never needed — only a `(body, hmac)` pair is replayed with a modified header. No credentials belonging to the victim are required, and the webhook endpoint is a public, unauthenticated HTTP endpoint by design.

### Recommendation
Include `shop_domain` (and `topic`, `api_version`, `webhook_id`) in the HMAC-signable payload, or otherwise cryptographically bind the shop identity to the signed body (e.g., have `HmacValidator` verify a canonical string composed of body + shop header, not raw body alone). At minimum, document prominently that `Webhooks::Request#shop`/`#topic` are NOT covered by HMAC verification, so host applications do not treat them as trusted after `HmacValidator.validate` succeeds.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `customers/data_request`), capturing the raw POST body and the `x-shopify-hmac-sha256` header value sent by Shopify (both are legitimate, signed with the real app `client_secret`).
2. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body`. [5](#0-4) 
4. The app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, and performs shop-scoped actions (e.g., data deletion/redaction, or looking up and using `victim-shop`'s stored access token) attributing them to the victim tenant.

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
