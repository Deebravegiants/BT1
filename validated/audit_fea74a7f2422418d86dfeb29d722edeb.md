### Title
Webhook `shop-domain` header is not covered by the HMAC signature, breaking the shop-authenticated-vs-shop-acted-upon binding - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by checking the HMAC over the raw request body only, but then trusts the `shop-domain` header — which is entirely outside the HMAC's coverage — as the authenticated tenant identity that is handed to the app's webhook handler.

### Finding Description
`Webhooks::Request` implements `VerifiableQuery` and defines `to_signable_string` as just the raw body: [1](#0-0) 

`hmac` is likewise derived purely from the `hmac-sha256` header, decoded/hex-encoded, with no binding to any other header: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate`, which computes `HMAC(secret, to_signable_string)` and compares it to `request.hmac`: [3](#0-2) [4](#0-3) 

Once the signature check passes, `Registry.process` reads `request.shop` — sourced directly from the `shop-domain` header — and passes it into `WebhookMetadata`, which is delivered to the host application's handler as the authenticated shop for that webhook: [5](#0-4) [6](#0-5) 

The documented usage pattern shows apps trusting `data.shop` directly to key work such as job enqueuing by shop domain: [7](#0-6) 

The broken binding, stated as an equality that the gem fails to enforce:
`shop identity cryptographically bound to the signed payload == shop identity delivered to the handler as `data.shop``

Because `to_signable_string` only returns `@raw_body`, the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are not part of the signed material at all. The HMAC secret (`api_secret_key`) is an app-level secret shared across every shop that has the app installed — it is not per-shop. Therefore any shop on which the app is installed can generate a body + valid HMAC pair (by triggering a real webhook event on its own store), and that same `(body, hmac)` pair remains valid for the app's HMAC check regardless of which `shop-domain` header is attached to the request, since that header is never hashed.

### Impact Explanation
This crosses a tenant boundary: an attacker who controls one shop with the app installed can capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair from a webhook triggered on their own store, then replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain (and/or a different `topic`/`webhook-id`). `Registry.process` will pass HMAC validation (body+hmac still match) and hand the host application a `WebhookMetadata` claiming to be from the victim shop, with attacker-controlled body content. Any host application following this gem's documented pattern (using `data.shop` to key session lookups, job queues, or per-tenant state, per `docs/usage/webhooks.md`) will process attacker-supplied data under the identity of a shop the attacker does not control — a cross-tenant data injection/confusion condition.

### Likelihood Explanation
Requires only that the attacker have the app installed on at least one shop they control (an unprivileged, ordinary merchant capability) and can trigger any webhook event on that shop to obtain a valid `(body, hmac)` pair — no access to `api_secret_key`, tokens, or victim credentials is needed. The header rewrite is a simple HTTP header modification. Likelihood is high given the low bar to reach the vulnerable code path.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the HMAC-covered signable string, or otherwise cryptographically tie the claimed `shop-domain` header to the verified payload before it is trusted, e.g.:

```diff
# lib/shopify_api/webhooks/request.rb
sig { override.returns(String) }
def to_signable_string
- @raw_body
+ "#{shop}\n#{topic}\n#{@raw_body}"
end
```
along with corresponding changes to how the HMAC is computed/verified, so that the `shop` value delivered to `WebhookMetadata` is provably the same one that was signed.

### Proof of Concept
1. App is installed on `attacker.myshopify.com` (attacker is an ordinary merchant, no special access needed).
2. Attacker triggers any subscribed webhook topic (e.g. `orders/create`) on their own shop, capturing the raw POST body `B` and the valid `x-shopify-hmac-sha256` header `H` computed by Shopify using the app's shared `api_secret_key`.
3. Attacker POSTs to the app's webhook endpoint with:
   - `x-shopify-hmac-sha256: H`
   - body: `B`
   - `x-shopify-shop-domain: victim.myshopify.com` (rewritten)
4. `ShopifyAPI::Webhooks::Request#hmac` reads `H`; `HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches `H`, so validation succeeds [8](#0-7) .
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, and invokes the host handler [9](#0-8) .
6. The host application, following the gem's documented pattern, processes this as legitimate data for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
