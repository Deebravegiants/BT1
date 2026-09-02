This confirms the vulnerability is concrete and library-documented: the gem explicitly hands `data.shop` to the app's handler as a trusted tenant identifier, with the documented example directly using `data.shop` for tenant-scoped work (`shop_domain: data.shop`), while the cryptographic verification only covers the raw body.

### Title
Webhook shop-domain identity spoofing — HMAC only signs the body, not the `shop` field passed to handlers - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop once `Utils::HmacValidator.validate(request)` succeeds, then forwards `request.shop` (read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) to the app's handler as the tenant identity. However, the HMAC only signs the raw request body, never the shop header, breaking the equality "shop authenticated == shop acted upon."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Utils::HmacValidator.validate_signature` computes the HMAC over exactly that signable string and compares it to the `hmac` field: [2](#0-1) . `Registry.process` gates only on this body-HMAC check, then builds `WebhookMetadata` directly from `request.shop`, which is read verbatim from the `shop-domain` header with no cryptographic binding to the signature: [3](#0-2)  and [4](#0-3) .

Because the webhook signing secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is shared across every merchant that installs the app rather than being per-shop, any merchant who has installed the app can obtain a validly-HMAC-signed body (e.g. by triggering any webhook event in their own store, or replaying a previously captured legitimate webhook body). That attacker can then resend the identical raw body with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still passes because it only checks the body bytes against the secret, yet `WebhookMetadata#shop` (and therefore whatever tenant-scoped action the host app performs, per the documented usage `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) now reports the victim's domain: [5](#0-4) .

This is the exact identity-binding break called out in scope: "a field acted on but not covered by the HMAC" — here the `shop` field is acted upon (used as the tenant key for all downstream processing) while only the body bytes are covered by the signature.

### Impact Explanation
Any app built with this gem that uses `data.shop` from `WebhookMetadata` to key tenant-scoped writes, job dispatch, or session/data lookups (as the gem's own documented example does) is exposed to cross-tenant data injection: a low-privilege merchant (any installer of the app) can make the host application believe webhook data belongs to a different merchant's shop, causing state to be written under, or actions performed against, another tenant's record. This satisfies the Critical bar of "cross-tenant access."

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate but unprivileged installer of the target app (no `api_secret_key`, no stolen token, no TLS interception needed) — they already legitimately possess the ability to generate a validly-signed webhook body for their own shop, and only need to replay it with a modified header, which any client fully controls when POSTing to the app's webhook endpoint. The gem provides no cross-check between the signed body and the shop header, and its own example code (`docs/usage/webhooks.md`) demonstrates the vulnerable pattern of trusting `data.shop` directly.

### Recommendation
`Registry.process` / `Utils::HmacValidator` should not be the sole trust anchor for shop identity. At minimum, the gem should document prominently (and ideally provide a helper) making clear that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host app against a shop it already has a legitimate, previously-established session/webhook-id record for, rather than trusted as an identity claim on its own. Where feasible, incorporate the shop domain into the value that is verified (e.g., requiring callers to additionally confirm `webhook_id`/topic uniqueness per known shop) before allowing `data.shop` to drive tenant-scoped side effects.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), capturing the raw POST body and its legitimate `x-shopify-hmac-sha256` value sent to the app's webhook endpoint.
2. Attacker resends an HTTP POST to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only [6](#0-5)  — validation succeeds because the shared `api_secret_key` and body are unchanged.
4. The handler receives `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim-shop.myshopify.com"` even though the body actually originated from the attacker's own store, allowing the host app's tenant-scoped logic to act on the attacker's payload as if it belonged to the victim.

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
