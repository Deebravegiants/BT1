### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant (shop) spoofing via webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC over the request, then trusts the `shop-domain` header as the tenant identity that gets handed to the host application's handler. The HMAC signature, however, is computed only over the raw request body, not over the `shop-domain` header. This breaks the identity binding `verified_bytes == acted_upon_identity`, analogous to the reported `Sender` binding failure in the external report (a field used for downstream trust decisions that is not covered by the same authentication mechanism that gates access).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC and, once it passes, forwards `request.shop` unchanged to the app-supplied handler as the authoritative tenant identifier: [3](#0-2) [4](#0-3) 

The HMAC validator only checks `computed_signature == received_signature` where the computed signature is derived from `to_signable_string`: [5](#0-4) 

Because the signature never binds to the `shop-domain` header, the equality that should hold is:

`verified(raw_body, hmac) == true` implies `shop == shop_that_sent(raw_body)`

but the gem only proves the left side and silently assumes the right side. An attacker who has legitimately received *any* valid `(raw_body, hmac)` pair from Shopify (e.g., by installing their own free/dev store and capturing a real webhook delivery to a shop they control) can replay that exact body+hmac to the target app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (it only checks the body against the secret), and `Registry.process` passes the forged `shop` value straight into `WebhookMetadata`, which the host application uses to select/act on tenant data. This is a cross-tenant confusion attack that requires no possession of the victim's access token, `api_secret_key`, or any other credential — only a valid, replayable (body, hmac) pair, which any unprivileged developer with any store can obtain from Shopify's own delivery mechanism.

### Impact Explanation
This crosses the tenant boundary explicitly called out in the rules ("a shop authenticated versus the shop stored as a session key"). A malicious actor can trick a merchant app into treating attacker-controlled webhook data (product updates, order data, `customers/redact`/GDPR payloads, app-uninstall notifications, etc., depending on which topics the host registers) as if they originated from a victim shop, or vice versa, cause the app to update/act on the wrong tenant's records. This satisfies the Critical bar of "cross-tenant access" since the shop identity binding used to route/attribute the webhook is forgeable without any credential belonging to that shop.

### Likelihood Explanation
The prerequisite (capturing one legitimately-signed body+hmac pair) is trivial for any unprivileged internet user: create a free Shopify development store, subscribe an endpoint you control to any webhook topic, and Shopify will deliver a validly-signed `(raw_body, hmac)` pair. The only extra step is sending that pair to the victim app's webhook endpoint with a forged `shop-domain` header — something entirely under the attacker's control since the header is never authenticated. No rate limiting, secret material, or social engineering is required.

### Recommendation
Include the shop domain (and ideally the topic/webhook-id/api-version) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before trusting `request.shop`. At minimum, document that `Registry.process`/`WebhookMetadata#shop` is not itself authenticated and that host apps must independently verify the `shop` value (e.g., against their own registered webhook subscriptions per shop) before using it to select tenant data.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com`, triggering delivery of a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` using the app's real `api_secret_key`, computed by Shopify — attacker never needs to know the secret).
2. Attacker replays the exact `raw_body = B` and `hmac header = H` to the same app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-computes the HMAC over `B` and finds it matches `H` — validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, and is passed to the app's handler as an authenticated fact (`lib/shopify_api/webhooks/registry.rb:198-199`).

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
