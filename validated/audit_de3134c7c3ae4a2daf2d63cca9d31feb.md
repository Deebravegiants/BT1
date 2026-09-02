Confirmed. The `VerifiableQuery` interface (`lib/shopify_api/utils/verifiable_query.rb`) only requires `hmac` and `to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor is read from the `x-shopify-shop-domain` header independently and is never mixed into the signed bytes [2](#0-1) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e., body only) before trusting `request.shop` to build `WebhookMetadata` passed to the handler [3](#0-2) .

### Title
Webhook `shop` domain is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, while the `shop` field that identifies which tenant the payload belongs to is taken from an unsigned HTTP header and forwarded unchecked to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the HMAC exclusively over that string [4](#0-3) . The `shop` value read by `Request#shop` comes from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is completely independent of the signed bytes [2](#0-1) . `Registry.process` checks only `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop` to construct the `WebhookMetadata` delivered to the app's registered handler [3](#0-2) .

Because the same `client_secret`/HMAC key is shared across every shop that installs the app, any merchant who installs the app on their own store (an unprivileged actor with respect to other tenants) legitimately receives real webhook deliveries with a valid `(body, hmac)` pair for their own shop. Since the HMAC never binds `shop`, that same `(body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop. `HmacValidator.validate` will return `true` because it only re-hashes the (unchanged) body, and `Registry.process` will hand the attacker-supplied `shop` value straight to the handler as if Shopify itself asserted that binding.

This breaks the intended equality: `shop asserted in WebhookMetadata == shop that Shopify actually signed for`. In reality it only guarantees `hmac(body) == hmac(body)`; `shop` is out-of-band and attacker-controlled.

### Impact Explanation
This allows cross-tenant data injection: an attacker-controlled webhook body (from their own legitimately-installed shop) can be attributed to any other shop of the attacker's choosing when passed to the app's webhook handler via `WebhookMetadata#shop` [5](#0-4) . Depending on how the host app keys its per-shop processing (order updates, GDPR/mandatory topics, inventory changes, etc.) off `WebhookMetadata#shop`, this can lead to cross-tenant state corruption or unauthorized actions performed against another merchant's store context — a tenant isolation break rooted entirely in this gem's webhook verification logic, since the gem presents `shop` as if it were authenticated alongside the body.

### Likelihood Explanation
Requires only that the attacker have installed the app on any shop they control (unprivileged, standard install) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed. This matches the documented processing flow in `docs/usage/webhooks.md` exactly (`Registry.process(Request.new(raw_body:, headers:))`) [6](#0-5) .

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) header values as part of the HMAC-signable bytes checked in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop domain to the verified payload, so that `HmacValidator.validate` fails if the shop header is altered relative to the shop the payload was actually generated for.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a real webhook: `POST /webhook` with body `B`, header `x-shopify-hmac-sha256: H` (valid for `B`), and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `(B, H)`.
3. Attacker sends `POST /webhook` to the same app endpoint with identical body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only hashes `B` [1](#0-0) .
5. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed_body_of_B, ...)` [5](#0-4) , letting the attacker inject data attributed to `victim.myshopify.com` despite never controlling that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L128-134)
```markdown
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
```
