Based on the analysis, I've identified a valid analog vulnerability that matches the required bug pattern: a field acted upon (the `shop-domain` header) that is not covered by the HMAC signature.

### Title
Webhook Shop Domain Spoofing via HMAC Scope Mismatch Enables Cross-Tenant Webhook Injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` field from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while `to_signable_string` — the value actually protected by the HMAC signature check in `ShopifyAPI::Webhooks::Registry.process` — covers only the raw request body. This breaks the equality `hmac-verified bytes == bytes acted upon for tenant identification`, allowing an attacker who controls one shop's genuine webhook deliveries to relabel them as belonging to a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` reads the signature from the `hmac-sha256` header, and `#to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor, however, is read straight from the `shop-domain` header without any cryptographic binding to the signed content [2](#0-1) .

`Registry.process` verifies the HMAC over the request via `Utils::HmacValidator.validate(request)` — which calls `request.to_signable_string` (the raw body) — and, once validated, immediately trusts `request.shop` to construct the `WebhookMetadata` handed to the app's handler: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [3](#0-2) . `HmacValidator.validate_signature` only performs `OpenSSL.secure_compare` between the header HMAC and the HMAC computed over `to_signable_string` (the body) using the app's shared `api_secret_key` [4](#0-3) . The `api_secret_key` is a single value shared by the app across all installed shops (it is not shop-specific), and it is the same secret Shopify itself uses to sign every webhook delivery for every shop that has the app installed.

Because the shop identity is delivered out-of-band from the signed payload, any entity that has installed the app on shop A — an ordinary, unprivileged merchant/tenant with respect to the app — can capture one legitimately-signed webhook delivery (raw body + valid `hmac-sha256`) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to shop B's domain. The HMAC check still passes because it never examined the shop header, and the app's handler consumes `data.shop` as an authenticated tenant identifier: the documented handler contract explicitly treats `data.shop` as "The shop domain of the webhook" [5](#0-4)  and `WebhookMetadata` is a typed struct with no verification tying `shop` back to the HMAC-covered bytes [6](#0-5) .

This is structurally the same class of bug as the report's "first mover" issue: a value that is trusted and acted upon (tenant/shop identity) is not actually covered by the mechanism (HMAC) meant to guarantee its authenticity, letting one tenant's authenticated action be misattributed to another tenant.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem that uses `data.shop` from `WebhookHandler#handle` to select which merchant's records to create/update/delete (a documented, expected usage pattern shown in the gem's own docs, e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [7](#0-6) ) can be made to apply attacker-supplied webhook content to a victim shop's tenant scope. This qualifies as cross-tenant access under the Critical impact category, since the gem's own signature-verification abstraction (`HmacValidator.validate`) gives host applications a false assurance that the entire `Request`, including `shop`, is authenticated.

### Likelihood Explanation
Exploitation only requires that the attacker be a legitimate, unprivileged installer of the target app on their own shop (no special credentials, no access token, no `api_secret_key` knowledge needed) — they merely capture one of their own webhook deliveries (available to anyone who controls the receiving endpoint or a network capture of their own traffic) and resend it with a modified header field. This is a low-effort, directly reachable path through the gem's documented webhook-processing API.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string, or otherwise require the host application to independently corroborate `request.shop` against a shop that is known to have the specific `webhook_id`/subscription registered, rather than trusting the header value once the body-only HMAC passes.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both registered for the same webhook topic (e.g., `customers/data_request`) pointing at the app's shared endpoint.
2. Shopify delivers a webhook to the app for `attacker-shop.myshopify.com`: body `B`, headers include `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` using the app's `api_secret_key`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. The attacker (who fully controls their own shop and can intercept/capture their own inbound webhook traffic) resends the exact same body `B` and `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and compares to `H` — validation succeeds because `B` and `H` are unchanged [8](#0-7) .
5. `WebhookMetadata.new(... shop: request.shop ...)` now reports `shop: "victim-shop.myshopify.com"` even though the payload never originated from or was authenticated for that shop, and the app's handler processes/persists it as victim-shop data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
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
