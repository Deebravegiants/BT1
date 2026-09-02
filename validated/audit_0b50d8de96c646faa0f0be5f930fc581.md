This confirms the key finding: the gem's documentation explicitly instructs developers to trust `data.shop` (line 25-26 of `docs/usage/webhooks.md`) for downstream per-tenant routing, while `ShopifyAPI::Webhooks::Registry.process` only validates the HMAC over the raw body, never binding it to the `shop-domain` header.### Title
Webhook `shop-domain` header is trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw JSON body, but the `shop` field it hands to the app's handler — the value used to identify *which tenant* the event belongs to — is read from an HTTP header that is completely outside that HMAC's coverage.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` is decoded from the `x-shopify-hmac-sha256`/`shopify-hmac-sha256` header: [1](#0-0) [2](#0-1) 

`Registry.process` verifies only that HMAC before dispatching the handler, and forwards `request.shop` (also read straight from headers) into `WebhookMetadata` untouched: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the signature only from `verifiable_query.to_signable_string` (the raw body) and compare it with `OpenSSL.secure_compare`: [4](#0-3) 

The library's own documentation instructs integrators to trust `data.shop` for per-tenant handling (e.g. `shop_domain: data.shop`) without any further cross-check: [5](#0-4) 

**Root cause / broken identity binding:** the intended invariant is `shop header == shop the body/HMAC was actually generated for`. Because the `shop-domain` header is never part of the HMAC's signable string, the gem verifies "these bytes came from Shopify for *some* shop," but exposes to the app "this event is for shop X" as if that assertion were equally authenticated. These are not the same claim, and the gem provides no API to bind them.

### Impact Explanation
An attacker who can install the target app on their own (attacker-controlled) Shopify store — an ordinary, unprivileged action available to any internet user via the Shopify App Store / dev store signup — will receive legitimate webhooks from Shopify for their own store, each with a valid `hmac` computed with the app's real `client_secret` over a body the attacker fully controls (they can trigger arbitrary orders/products/customers events in their own store). The attacker then replays that exact `(raw_body, hmac)` pair to the app's public webhook endpoint but substitutes the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and `WebhookMetadata.shop` now falsely claims to be the victim shop while `body` is attacker-controlled content. Any host application that follows the gem's documented pattern of using `data.shop` to select the tenant's session/DB record for processing the webhook body will process attacker-controlled data under the victim's tenant identity — a cross-tenant data-integrity/confusion issue reachable purely through this gem's authentication guarantee.

### Likelihood Explanation
High reachability: no privileged credentials, TLS interception, or social engineering are required — only the ability to install the app on a store the attacker controls (a normal, permissionless action) and to send one crafted HTTP POST to the app's public webhook route. The gem's own example code in `docs/usage/webhooks.md` demonstrates exactly the vulnerable usage pattern (dispatching work keyed on `data.shop`), meaning this is not a documented-but-ignored misuse — it is the intended integration point of the API, and the gem itself provides no mechanism (e.g., binding shop to the signed payload, or requiring the caller to cross-check `shop` against an expected/registered value) to prevent it.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in the HMAC-signable string, or otherwise cryptographically bind the claimed shop to the verified payload, so `Registry.process` can detect a shop/body mismatch before constructing `WebhookMetadata`. At minimum, `Registry.process` should require the caller to supply the shop domain(s) it expects for the given webhook route/registration and reject requests whose header `shop` does not match a shop known to have that webhook registered, rather than passing the raw, unauthenticated header straight through to the handler.

### Proof of Concept
1. Attacker installs the victim app on their own dev store `attacker.myshopify.com`, obtaining a valid access token and receiving real webhook deliveries.
2. Attacker triggers an `orders/create` event in their own store, capturing the legitimate request: `raw_body = B`, `x-shopify-hmac-sha256 = HMAC(client_secret, B)`, `x-shopify-shop-domain = attacker.myshopify.com`.
3. Attacker POSTs to the app's public webhook endpoint (`ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)` → `ShopifyAPI::Webhooks::Registry.process`) but replaces the `x-shopify-shop-domain` header with `victim.myshopify.com`, leaving `B` and the HMAC header untouched.
4. `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` — identical to the captured value — and passes, per `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` per `lib/shopify_api/webhooks/registry.rb:198-199` and invokes the app's handler, which (per the gem's documented usage) processes attacker-supplied `body` as though it were a genuine event for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
