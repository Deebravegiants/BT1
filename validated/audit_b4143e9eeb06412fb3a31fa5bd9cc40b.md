### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator.validate`, which computes and compares the HMAC only over `to_signable_string`, i.e., the raw request body [1](#0-0) . The `shop` accessor, however, is derived entirely from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which plays no part in the signed payload [2](#0-1) . `Registry.process` trusts this header value as the tenant identity and forwards it directly to the app's webhook handler as `WebhookMetadata#shop` [3](#0-2) [4](#0-3) . Host apps are documented to key business logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) off this `data.shop` value [5](#0-4) .

This mirrors the analog rule of "a field acted on but not covered by the HMAC": the field that determines *which tenant* an event belongs to (`shop`) is disjoint from the field that is cryptographically authenticated (`raw_body`).

### Finding Description
`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac` [6](#0-5) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `hmac` is read from the `hmac-sha256` header [7](#0-6) .

The identity binding this is supposed to enforce is: `hmac == HMAC(secret, body_bound_to_shop)`. But in reality it only proves `hmac == HMAC(secret, body)` — it says nothing about which shop the body is associated with, because `shop` comes from a separate, unsigned header field [2](#0-1) .

Any entity that can obtain one genuinely-signed `(raw_body, hmac)` pair for the target app (e.g., by installing the app on their own store and receiving a legitimate webhook delivery, since HMAC secret is shared across all shops using the app) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it only checks the body against the signature, never checking that the `shop` header itself is bound to that signature [8](#0-7) . The forged request is then dispatched to the handler with an attacker-chosen `shop` value trusted as ground truth [9](#0-8) .

### Impact Explanation
This breaks tenant isolation ("cross-tenant access", Critical per the given impact taxonomy). A host application that uses `data.shop` from `WebhookMetadata` to decide which merchant's records to update/read (exactly as shown in this gem's own documented usage pattern [5](#0-4) ) can be tricked into applying webhook payloads meant for the attacker's own shop against a victim shop's tenant data, or vice versa — because the gem asserts the payload came from `shop` X while only having proven it came from *some* shop that shares the app's `client_secret`.

### Likelihood Explanation
Any unprivileged actor who can install the app on a shop they control (a normal, unprivileged, self-service action for any public/embedded Shopify app) automatically receives genuinely-signed webhook deliveries with a valid `hmac-sha256` header computed with the shared app secret. Replaying the identical `raw_body` + `hmac-sha256` header combination with a forged `shopify-shop-domain` header requires no secret knowledge and no privileged access — it only requires the ability to send an HTTP POST to the app's public webhook callback URL, which by design is unauthenticated (the HMAC check *is* the authentication).

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the material verified by the HMAC, or otherwise cryptographically bind them to the request. Concretely:
- Include `shop-domain` in `to_signable_string` (or in the value passed to `HmacValidator`), similar to how `Auth::Oauth::AuthQuery#to_signable_string` incorporates `shop` into what is signed [10](#0-9) , so that changing the `shop` header invalidates the signature.
- Alternatively, document/require that host apps cross-check `data.shop` against a shop they already have an active, previously-established session/installation for, rather than trusting it as self-authenticating.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic (e.g. `orders/create`) so Shopify delivers a legitimately HMAC-signed webhook POST to the app's callback URL, capturing `raw_body` and the `x-shopify-hmac-sha256` header value.
2. Replay the exact same POST to the app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `raw_body` and matches the (unchanged) signature [8](#0-7) [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [9](#0-8) , causing the host app (per its documented pattern of trusting `data.shop`) to process the attacker's payload as if it belonged to `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
