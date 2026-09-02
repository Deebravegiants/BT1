### Title
Cross-tenant webhook shop spoofing — `WebhookMetadata.shop` is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, so the HMAC that `ShopifyAPI::Webhooks::Registry.process` validates covers **only the body bytes**. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which are parsed unauthenticated and forwarded straight into `WebhookMetadata` for the app's business logic — are never part of the signed material. This breaks the intended identity binding: `hmac verifies body` ≠ `shop used by handler.handle`.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header, and `Request#to_signable_string` returns `@raw_body` alone: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled directly from HTTP headers without any cryptographic binding to that signed body: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` (which hashes only `to_signable_string`, i.e. the body) and then, once that check passes, dispatches to the app's registered handler using `request.shop` and the other unauthenticated headers: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the digest purely from `verifiable_query.to_signable_string`: [4](#0-3) 

The documented app integration pattern explicitly trusts `data.shop` for per-tenant processing (e.g., enqueuing shop-scoped jobs): [5](#0-4) 

Because the app's `api_secret_key` is a single shared secret for the whole app across **all** installed shops (not shop-specific), any user who has legitimately installed the app on their own shop receives real webhooks with valid `(body, hmac)` pairs signed with that shared secret. Since the header set (`shop-domain`, `topic`, `webhook-id`, `api-version`) is excluded from the signed string, that same attacker can resend the identical raw body and identical `hmac-sha256` header value to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. `HmacValidator.validate` still returns `true` because it never inspects the headers, and `Registry.process` forwards the forged `shop` value to the app's handler as if it were an authentic event from the victim's tenant.

This is the identity-binding violation this report class calls out: a field the application acts upon (`shop`, used for tenant identification/routing) is not covered by the HMAC that ostensibly authenticates the request, exactly analogous to `_unsettled` being scaled by a factor that should only apply elsewhere — here, the signature validates the wrong thing (body only) while a different, unauthenticated field (`shop`) drives privileged, tenant-scoped behavior.

### Impact Explanation
**High.** An attacker who is merely a legitimate (if malicious) installer of the app — requiring no stolen access token, no `api_secret_key`, and no privileged access to any other merchant's shop — can make the app process forged webhook events attributed to an arbitrary victim shop domain. Depending on what the app's `WebhookHandler#handle` implementation does with `data.shop` (e.g., look up that shop's session/access token and act on its behalf, write/delete shop-scoped data, trigger app-side automation), this can result in cross-tenant data corruption, cross-tenant workflow triggering, or misattributed actions against another merchant's store — a cross-tenant confused-deputy condition entirely enabled by this gem's request-verification design.

### Likelihood Explanation
**High.** Any internet user can install a public app to obtain one legitimate `(raw_body, hmac-sha256)` pair from Shopify, then simply replay that exact body/HMAC to the app's same public webhook endpoint with a modified `X-Shopify-Shop-Domain` (and optionally `topic`/`webhook-id`) header. No cryptographic secret needs to be known or brute-forced — the attacker only needs a header value they already legitimately received.

### Recommendation
Include the identity-relevant headers (`shop-domain` at minimum, ideally `topic` and `webhook-id` too) in the signed material used for HMAC verification, or otherwise cryptographically bind them to the body before trusting them (e.g., require the app to independently verify the shop is one it has an active, registered subscription for that specific webhook `topic`/`webhook_id`, and treat the header-derived `shop` as untrusted until corroborated). At minimum, `to_signable_string` should not diverge from what Shopify actually signs versus what is dispatched to handlers as trusted identity data.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify POSTs a real, validly-signed webhook to the app's public endpoint. Capture the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (computed by Shopify over `B` using the app's shared `client_secret`).
2. Replay an HTTP POST to the same app endpoint with:
   - Body: identical `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (arbitrary, attacker-chosen)
   - Header `X-Shopify-Topic`/`X-Shopify-Webhook-Id` optionally altered as well.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body` [1](#0-0) .
4. The app's `WebhookHandler#handle` is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , causing the app to perform shop-scoped work under the wrong tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
