## Title
Webhook shop identity spoofing via HMAC that only signs the raw body, not the `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from `@raw_body`, while the `shop` identity used downstream by the handler is read from an unauthenticated HTTP header (`x-shopify-shop-domain` / `shopify-shop-domain`). Because the app's webhook HMAC secret (`Context.api_secret_key`) is shared across every shop that installs the app, a valid `(body, hmac)` pair obtained from a webhook Shopify legitimately sends for one shop can be replayed to the same endpoint with a forged shop-domain header claiming to be a different (victim) shop. `Utils::HmacValidator.validate` will accept it because it only verifies the body's authenticity, not which shop it belongs to.

### Finding Description
The `to_signable_string` implementation only returns the raw request body: [1](#0-0) 

The shop identity, however, comes from a header that is never included in that signable string: [2](#0-1) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., just the body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` performs this HMAC check and then unconditionally trusts `request.shop` when building the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The identity binding that is broken is:
`shop authenticated by the HMAC signature` (none — the signature only covers `@raw_body`) `≠` `shop the handler is told the webhook came from` (`request.shop`, taken from an attacker-controllable header).

Since the app's `api_secret_key` is a single, app-wide secret shared by all merchants who install the app (not a per-shop secret), a `(body, hmac)` pair that is valid for one installation is also a cryptographically valid pair for every other shop's webhook endpoint of the same app. Any unprivileged internet user can become a legitimate "shop" simply by installing the target app on their own (free) Shopify development store, causing Shopify to send them genuinely-HMAC-signed webhook payloads. The attacker can then replay that exact body/HMAC to the app's public webhook callback URL while substituting the `x-shopify-shop-domain` header with a victim shop's domain. The gem-level validation in `HmacValidator.validate`/`Registry.process` will report the webhook as valid and hand the handler a `WebhookMetadata` claiming `shop: <victim>`.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem provides no mechanism to cryptographically bind the claimed shop to the verified payload, so any host application that follows the gem's own documented usage pattern (using `data.shop` from `WebhookMetadata` to select which merchant's record to update/enqueue work for — as shown in the gem's own webhooks.md example) can be tricked into acting on a victim shop's behalf with attacker-chosen webhook content. Depending on the topic replayed (e.g., `app/uninstalled`, `shop/update`, `customers/redact`, or any topic the attacker can trigger on their own store), this can lead to unauthorized state changes, data deletion, or corruption attributed to a shop the attacker does not control — a cross-tenant access impact.

### Likelihood Explanation
Any internet user can create a free Shopify development store and install a public app to receive real, validly signed webhooks for topics the app subscribes to. Replaying the captured `(raw_body, hmac header)` pair with a substituted `shop-domain` header requires only a basic HTTP client; no access token, `client_secret`, or privileged account is required. The only prerequisite is that the app's webhook endpoint is reachable, which is true by design (Shopify webhook callback URLs are public).

### Recommendation
Bind the shop (and ideally the topic/webhook-id) into the signed material, or otherwise verify that the shop claimed in the header matches an expected/registered shop before trusting it — e.g., by validating the header's shop domain via `ShopValidator` and cross-referencing it against the app's stored installation for that HMAC/secret pair, or by requiring hosts to independently confirm the shop is one they have an active session/installation for before acting on `WebhookMetadata#shop`. At minimum, document prominently that `request.shop` is not covered by the HMAC and must not be trusted as an authenticated tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a store they fully control) and enables a webhook topic the app handles (e.g., `orders/create`).
2. Shopify sends a legitimately signed webhook to the app's endpoint: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` using the app's shared `api_secret_key`), `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker replays the exact same request to the same endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H` unchanged, but sets `x-shopify-shop-domain = victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` — validation succeeds.
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and any app logic keyed off `data.shop` now operates against the victim's tenant using attacker-supplied body content.

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
