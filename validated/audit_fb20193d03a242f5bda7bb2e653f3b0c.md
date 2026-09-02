Confirmed: `WebhookHandler.handle` is called with `data.shop` taken directly from the request header, and Shopify's own app framework (`shopify_app`) docs recommend using `data.shop` to identify the tenant, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`. This is a real, exploitable identity-binding gap in this gem's webhook processing path.

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `topic`, `shop`, `api_version`, and `webhook_id` fields directly from unauthenticated HTTP headers, while `Utils::HmacValidator.validate` only verifies the HMAC over `to_signable_string`, which returns nothing but the raw request body. The `shop` value handed to the application's `WebhookHandler` is therefore never covered by the cryptographic signature, breaking the equality that should hold: `shop attributed to a processed webhook == shop that produced the signed body`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with no relation to the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (the body), never incorporating headers: [3](#0-2) 

`Registry.process` then trusts `request.shop` unconditionally and forwards it to the app-registered handler as the tenant identifier: [4](#0-3) 

Because the `api_secret_key` used for the HMAC is a single value shared across every shop that has installed the app (it is not shop-specific), a valid `(raw_body, hmac)` pair produced for one installed shop remains cryptographically valid no matter which `shop-domain` header accompanies it. An attacker who controls one legitimately installed shop (e.g. a free/dev store) can capture a real webhook delivery for their own shop and resend the identical body and HMAC to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header rewritten to a victim shop. `Utils::HmacValidator.validate` reports success because the body/HMAC pair is genuinely valid, and `Registry.process` builds `WebhookMetadata` claiming the victim shop, which is exactly what the documented handler pattern uses to key subsequent tenant actions such as `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`. [5](#0-4) 

This mirrors the report's bug class precisely: just as `vault_gkhan_account` was validated only by `owner`/`mint` without binding to how the account was actually created (allowing a phantom, attacker-controlled account to be swapped in for a legitimate one), here the `shop` identity is validated only by presence-of-header, without being bound to the signature that authenticates the payload it travels with — allowing an attacker-controlled tenant label to be swapped onto a legitimately-signed payload.

### Impact Explanation
This allows cross-tenant confusion in any application built on this gem's documented webhook pattern: an attacker-controlled webhook body can be attributed to a victim shop with a cryptographically "valid" signature. Depending on the topic (e.g. `app/uninstalled`, `shop/update`, `customers/data_request`), this can trigger tenant-scoped side effects (session/token deletion, data processing, compliance actions) against a shop the attacker does not control, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only: (1) the attacker legitimately installs the target app on any shop they control (a normal, low-privilege action available to any Shopify merchant/dev-store owner), (2) captures one real webhook delivery Shopify sends them, and (3) replays it to the app's public webhook endpoint with a modified `shop-domain` header. No knowledge of `api_secret_key` or access to the victim's credentials is needed, and the vulnerable code path (`HmacValidator.validate` / `Request#shop`) is exercised on every webhook the gem processes.

### Recommendation
Bind the shop identity to the signed content, e.g. include the `shop-domain` (and ideally `topic`/`webhook_id`) header values in the string that is HMAC-verified, or independently verify that `request.shop` corresponds to a shop with an active session/installation known to the app before dispatching to the handler. At minimum, document that `WebhookMetadata#shop` is not cryptographically authenticated and must not be used as a sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receiving genuine Shopify webhooks signed with the app's `api_secret_key`.
2. Attacker captures one such delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker POSTs to the app's webhook endpoint reusing body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only checks `B` against `H`: [6](#0-5) 
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and dispatched to the app's handler, which acts on the victim shop using attacker-supplied body content.

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
