### Title
Webhook shop identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the shop identity used downstream to route/attribute the webhook is read from an unsigned HTTP header. Because a Shopify app's webhook HMAC secret (`api_secret_key`/`client_secret`) is shared across every shop that installs the app, an attacker who installs the app on their own shop can obtain a genuinely-signed `(body, hmac)` pair and replay it against the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read straight from an HTTP header that is never part of the signed material: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC of `to_signable_string` against `Context.api_secret_key` — a single secret shared by the app across all its installed shops: [3](#0-2) 

`Registry.process` trusts this validation and then forwards the unverified `request.shop` straight to the host app's handler as the tenant identifier: [4](#0-3) 

The equality the library implicitly claims to guarantee is:
`shop that produced the HMAC-valid bytes == shop delivered to the handler as WebhookMetadata#shop`

This equality does not hold: the HMAC only proves "some shop belonging to this app produced this body", not "this particular shop produced this body." Since `api_secret_key` is identical for every shop of the app, any shop-owning attacker can generate a validly-signed `(body, hmac)` pair (e.g., by triggering `orders/create` in their own store with attacker-chosen content), then POST that exact body/hmac to the shared webhook endpoint while substituting `X-Shopify-Shop-Domain` for a different, victim shop that also uses the app. `HmacValidator.validate` still returns `true` (the body/hmac pair is authentic), and `Registry.process` hands the handler a `WebhookMetadata` claiming the data originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to preserve: an app built on this gem cannot distinguish "authentic data from shop A" from "authentic data replayed and mislabeled as shop B." Any host application that keys its multi-tenant data model off `WebhookMetadata#shop` (the only tenant-identifying field the library exposes for webhooks, and the documented mechanism for doing so) can be made to attribute attacker-controlled webhook payloads to a shop the attacker does not own — a cross-tenant data-injection primitive.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on a shop the attacker controls (self-service, unprivileged — trial/dev stores are freely available), (2) triggering a webhook topic to obtain one genuine `(body, hmac)` pair, and (3) sending a direct HTTP POST to the app's known webhook URL with a substituted shop header. No access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Bind the trusted shop identity to the signed request instead of trusting the `X-Shopify-Shop-Domain` header alone. Practical mitigations for this gem:
- Include `shop` (and ideally `topic`/`webhook-id`) in the HMAC-signable string when the caller controls webhook subscriptions per-shop, or
- Cross-check `request.shop` against the shop associated with the webhook subscription identified by `webhook_id` before dispatching to the handler, or
- Document explicitly (and enforce where possible) that `WebhookMetadata#shop` is not cryptographically bound to the payload and must be independently re-validated (e.g., against a known active session for that shop) before being trusted as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` (app's `api_secret_key` is shared across all installs).
2. Attacker triggers a webhook (e.g. `orders/create`) with attacker-chosen order JSON; Shopify's real servers sign it with the app's shared secret, producing a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair.
3. Attacker captures this `raw_body` + `hmac` and issues a direct HTTP POST to the app's public webhook endpoint, keeping `raw_body`/`hmac` unchanged but setting `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (`lib/shopify_api/webhooks/request.rb`); `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because only `raw_body` is checked against the shared secret (`lib/shopify_api/utils/hmac_validator.rb:12-22`).
5. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker JSON>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing attacker-controlled data to be processed under the victim's tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
