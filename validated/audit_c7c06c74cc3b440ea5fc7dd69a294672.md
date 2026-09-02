### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) claims are trusted but not covered by the HMAC signature, allowing cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers and are never included in the signed material. `Registry.process` validates only that the body's HMAC is correct, then unconditionally forwards the caller-supplied `shop` header value to the app's handler. Any party capable of obtaining one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (e.g., by installing the app on their own store and receiving a real webhook) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, and the gem will treat the payload as authentic data belonging to that arbitrary shop.

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for webhooks that is defined as just the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers with no cryptographic binding to the signature at all: [2](#0-1) 

`Registry.process` verifies the HMAC and then hands `request.shop` straight to the app's handler as the tenant identity for the event, with no check that this shop is the one that actually produced the signed body: [3](#0-2) 

This is the same identity-binding failure pattern as the referenced report: a field that is acted upon (here, the `shop` used to attribute and process the webhook event) is not covered by the integrity check (the HMAC), while a different field (the raw body) is the only thing actually verified. Because Shopify apps share a single `api_secret_key`/`client_secret` across every merchant installation, any unprivileged actor who installs the public app on their own (even free/dev) store can trigger a real event, capture the resulting valid `(raw_body, hmac)` pair from their own store's webhook delivery, and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will call the handler with `shop: <victim shop>` and the attacker-controlled (but validly-signed) body content.

### Impact Explanation
This breaks the binding "the shop asserted for a webhook event == the shop that actually generated the signed body." An attacker with no privileges beyond a self-service app install can inject arbitrary attacker-chosen event payloads that the host application will process/store as if they originated from a different, victim merchant's shop — i.e., cross-tenant data injection/cross-tenant access, which the task rules classify as Critical impact.

### Likelihood Explanation
Exploitation only requires: (1) installing the target public app on an attacker-controlled store (a normal, unprivileged action available to any developer), (2) triggering any webhook event on that store to capture a valid `(body, hmac)` pair, and (3) POSTing that pair to the same app's webhook endpoint with a forged `shop-domain` header. No secrets, tokens, or elevated access are required, and the gem provides no header-shop-to-signature binding or replay protection to prevent it, so likelihood is high for any app that trusts `WebhookMetadata#shop` for tenant attribution (which is the gem's documented usage pattern).

### Recommendation
Include the shop domain (and ideally topic/webhook id, with a per-request nonce/timestamp check) in the signed material, or otherwise cryptographically bind the header-derived `shop` to the specific signed body before it's handed to application handlers. At minimum, `Registry.process` should verify that the shop claimed in the headers matches the shop the app expects for that HMAC-verified body (e.g., by having the caller supply the expected shop for the session/lookup and rejecting mismatches), rather than blindly trusting the unauthenticated `shop-domain` header.

### Proof of Concept
1. Attacker installs the public app on `attacker-shop.myshopify.com` and triggers an event (e.g., creates an order) that causes Shopify to send a webhook: `POST /webhook` with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and body `B`.
2. Attacker captures `B` and the valid `<valid-hmac-of-body>` (computed with the app's shared `api_secret_key`).
3. Attacker replays the exact same request to the app's webhook endpoint but changes only the header: `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) passes because it only checks `B` against the HMAC.
5. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the app handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, causing the host app to process/store forged data as belonging to the victim tenant.

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
