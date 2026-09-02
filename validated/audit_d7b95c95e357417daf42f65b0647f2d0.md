## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then trusts the `X-Shopify-Shop-Domain` header — which is **not** part of the signed payload — as the authoritative tenant (`shop`) identifier passed to the app's handler. This is the same "field acted on but not covered by the HMAC" class of bug as the reported `burst()` finding: the value used to make a security-relevant decision (which shop a webhook belongs to) is disjoint from the value actually authenticated (the raw body bytes).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

But `#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the signed content: [2](#0-1) 

`HmacValidator.validate` only recomputes and compares the signature against `to_signable_string` (the body): [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`, handing it to the app's handler as the tenant identity for the webhook: [4](#0-3) 

The documented handler usage pattern shows apps are expected to key their downstream logic/storage on `data.shop`: [5](#0-4) 

The broken binding, stated as an equality that should hold but doesn't:
`shop domain authenticated by HMAC` ≠ `shop domain delivered to the handler (X-Shopify-Shop-Domain header)`.

### Impact Explanation
Any unprivileged internet user who can obtain one legitimately signed webhook payload for *any* shop (e.g., by installing the same public app on their own free/dev store and capturing a real webhook delivery, whose body+HMAC they fully control the timing/replay of) can resend that exact `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` forwards the forged shop to `WebhookHandler#handle` as `WebhookMetadata#shop`. Any app following the gem's own documented pattern — routing/storing webhook data keyed by `data.shop` — will attribute attacker-controlled webhook data to the victim tenant. This is a cross-tenant data injection/confusion primitive achievable purely through the gem's public API, without any privileged credentials, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: exploitation requires no secrets, tokens, or privileged access — only a public app the attacker can install on their own store to obtain one valid, replayable `(raw_body, hmac)` pair, plus the ability to send an HTTP POST with an arbitrary `Shopify-Shop-Domain` header to the app's public webhook endpoint (which by design must be internet-reachable). No rate limiting or nonce/timestamp binding of `shop` to the signature prevents this replay.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind `request.shop` to the verified payload before it is trusted. At minimum, `Registry.process` (or `Request`) should refuse to accept the header-derived `shop` unless it can be independently corroborated (e.g., by cross-checking against a known/registered shop session, or by including the shop domain as part of `to_signable_string`) rather than passing it through unauthenticated to `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-SHA256` header value `H` that Shopify sent — both valid and signed with the app's shared `api_secret_key`.
2. Attacker sends a new POST request to the same app's public webhook endpoint with:
   - Body: exactly `B` (unchanged, so HMAC over the body still validates)
   - Header `X-Shopify-Hmac-SHA256`: `H` (unchanged)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (attacker-controlled/forged)
   - Header `X-Shopify-Topic`: same topic as captured
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because only `B` is checked.
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the forged `victim-shop.myshopify.com`.
5. The app's handler (per the documented pattern) processes/stores webhook data as belonging to `victim-shop.myshopify.com`, achieving cross-tenant data confusion/injection without any credential belonging to the victim.

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

**File:** docs/usage/webhooks.md (L19-29)
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
