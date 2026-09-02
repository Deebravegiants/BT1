### Title
Webhook `shop` (tenant identity) is not covered by the HMAC signature, allowing cross-tenant impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` authenticates the *body bytes* but never binds them to the `shop` (or `topic`/`webhook_id`) that the same request claims via the `x-shopify-shop-domain` header. `Registry.process` nonetheless treats `request.shop` as an authenticated tenant identifier and forwards it unchanged into `WebhookMetadata#shop`, which is handed to the host app's `WebhookHandler#handle`. This breaks the required equality: `shop authenticated by HMAC == shop used as tenant identity`.

### Finding Description
- `Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field of the `VerifiableQuery` implementer. [1](#0-0) 
- For webhooks, `Request#to_signable_string` returns `@raw_body` exclusively — the `shop`, `topic`, `api_version`, and `webhook_id` values (all sourced from HTTP headers, not from the signed body) are excluded from the signable string. [2](#0-1) 
- `Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.topic` and `request.shop` — taken straight from headers — to route the webhook and populate `WebhookMetadata`, which is passed to the app-supplied handler as the tenant/shop the event belongs to. [3](#0-2) 
- `WebhookMetadata#shop` is a plain `const :shop, String` with no cryptographic binding to the HMAC-verified payload, and `WebhookHandler#handle` receives it as ground truth. [4](#0-3) 

Because the app's `api_secret_key` (`client_secret`) is shared across every shop that installs the app, the HMAC only proves "this body was HMAC'd with our app secret" — it does not prove "this body came from shop X." An attacker who controls one installed shop (Shop A) can obtain a legitimate webhook body + valid HMAC for Shop A (from Shopify's real delivery, or by using a legitimate Shop A payload they control), and replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for Shop B. `Utils::HmacValidator.validate` still succeeds because it only checks the body's HMAC, and `Registry.process` will hand the app's handler a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` with attacker-controlled `body`. Any handler logic that trusts `data.shop` to scope database writes, cache invalidation, redaction, or entitlement changes to "the shop that owns this event" is now operating on attacker-chosen tenant identity with attacker-chosen body content — a cross-tenant identity-binding break of exactly the class described in the report (HMAC covers some bytes, but the field actually used as a security-relevant identity is not covered).

### Impact Explanation
This is a cross-tenant integrity/impersonation issue: an attacker with control of one installed shop can make the app process attacker-supplied event data as though it originated from a different, victim shop, without needing that shop's credentials. Depending on how the host app implements `WebhookHandler#handle` (which is outside this gem, but the gem's own API is what enables the confusion by not binding `shop` to the signature), this can lead to cross-tenant data corruption, spoofed mandatory compliance webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) being attributed to the wrong shop, or forged state transitions scoped to a victim tenant.

### Likelihood Explanation
Requires only an unprivileged attacker who can install the app as one tenant (or intercept/replay one legitimate webhook delivery) and can send arbitrary HTTP POSTs to the app's public webhook endpoint with forged headers and a previously-valid `(body, hmac)` pair — no access token, `client_secret`, or privileged account is needed. The gem itself performs no anti-replay or shop-binding check, so exploitation is a direct consequence of calling `Registry.process` as documented.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the request, e.g., by rejecting requests where headers were not part of the originally delivered, Shopify-signed payload), and treat `request.shop`/`WebhookMetadata#shop` as untrusted until such binding exists.

### Proof of Concept
1. App has two installed shops: `attacker-shop.myshopify.com` (attacker-controlled) and `victim-shop.myshopify.com`.
2. Attacker receives (or crafts, since they control the shop and can trigger events) a real webhook delivery to their own endpoint: raw body `B` with header `x-shopify-hmac-sha256: H` (valid for `B` under the shared `client_secret`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical `B`/`H` pair to the app's webhook endpoint, replacing only the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only hashes `@raw_body` (`Request#to_signable_string`), per [5](#0-4) .
5. `Registry.process` calls the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, per [6](#0-5) , even though the event data actually originated from the attacker's shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
