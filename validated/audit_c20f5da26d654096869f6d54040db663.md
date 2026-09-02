## Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant shop spoofing — (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (from the `X-Shopify-Shop-Domain` header) is never included in the signed material. `Registry.process` validates the HMAC and then blindly forwards the unauthenticated `shop` value to the app's webhook handler, breaking the binding "shop proven authentic by HMAC" == "shop delivered to the handler."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read from a separate, unsigned header: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC, so it never covers `shop`: [3](#0-2) 

`Registry.process` validates only this body-scoped HMAC, then constructs `WebhookMetadata` using the unauthenticated `request.shop`, and hands it to the app's handler with no further shop check: [4](#0-3) 

Because `shop` is excluded from the signed content, any party who legitimately receives one authentic, HMAC-valid webhook for their own shop (e.g., after installing the app on their own store) can capture that `(body, hmac)` pair and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (or `shopify-shop-domain`) with a victim shop's domain. The HMAC check still passes because it only validates the body/secret pair, which is untouched. The forged request is then processed as if it originated from the victim shop, breaking the identity binding: `shop authenticated by HMAC` ≠ `shop delivered to WebhookMetadata`.

This is analogous to the reported bug class ("a field acted on but not covered by the HMAC").

### Impact Explanation
If a webhook handler uses `WebhookMetadata#shop` to key data updates, trigger side effects, or scope tenant data (a common pattern, e.g. updating billing/status/inventory records for "this shop"), an attacker who has their own valid app installation can inject attacker-controlled webhook payloads that are processed under a victim shop's identity — a cross-tenant access primitive, which the rubric classifies as Critical impact.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to install the target app on any shop they control (a normal, unprivileged action for any Shopify merchant), capture one legitimate webhook (raw body + `X-Shopify-Hmac-Sha256`), and replay it with a modified shop-domain header to the app's public webhook endpoint. No access to the app's `api_secret_key` or any privileged credential is required.

### Recommendation
Include the shop domain (and topic/webhook-id) in the signed material used for webhook verification, or, at minimum, require webhook handlers/`Registry.process` to cross-check `request.shop` against the set of shops that have valid, stored sessions/installations for this app before dispatching to handlers. Do not treat `request.shop` as authenticated purely because the body HMAC validated.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures/observes a delivered webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, computed by Shopify using the app's shared secret over `B`).
2. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — matches `H`, so validation succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the HMAC never certified that shop value, allowing the attacker to make the app act as if the data pertains to the victim's shop.

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
