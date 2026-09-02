### Title
Webhook shop domain is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the tenant-identifying `shop` (and `topic`/`webhook_id`) values are read directly from HTTP headers that are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` validates only that the body's HMAC is correct and then dispatches the handler using the unauthenticated `shop` header. This mirrors the `LivenessGuard` bug class: an identity value that a security check is supposed to bind (the "owner"/tenant) is instead accepted from state that the check never actually covers, so it can be swapped out under attacker control while the underlying check still "passes."

### Finding Description
The webhook signable string is defined as just the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all parsed straight from headers, none of which participate in HMAC computation: [2](#0-1) 

`Registry.process` only checks the body HMAC, then immediately uses the unauthenticated `request.shop` to build the `WebhookMetadata` passed to the app's handler — there is no cross-check that the shop these bytes were actually signed for matches the shop claimed in the header: [3](#0-2) 

This is the same class of bug described in the LivenessGuard report: a piece of trusted state (`ownersBefore` in the analog; `shop`/`topic` here) that a validation step is assumed to protect is not actually covered by the binding check (`checkAfterExecution` HMAC-equivalent), so it can silently diverge from what was truly authenticated (the raw body content only).

### Impact Explanation
Any entity capable of triggering (or replaying) a legitimately HMAC-signed webhook body — for example, a merchant who has installed the app on their own store and thus routinely receives real, correctly-signed webhooks for their own shop — can resend that exact same body/HMAC pair to the app's webhook endpoint while altering only the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header. `HmacValidator.validate` still succeeds because it only re-derives the signature from `@raw_body`, and `Registry.process` will dispatch the handler with the attacker-chosen `shop` value. Because host applications built on this gem are expected to use `WebhookMetadata#shop` as the tenant key (e.g., to load the correct merchant's session/access token or to attribute writes), this allows cross-tenant confusion: data legitimately generated for shop A can be replayed and processed as if it belongs to shop B, without the attacker ever needing shop B's credentials.

### Likelihood Explanation
The barrier to exploitation is low relative to the required outcome: the attacker only needs access to any one legitimately signed webhook payload for a shop they control (trivially obtainable by installing the app and triggering the relevant event), then a single unauthenticated HTTP request to the same webhook endpoint with a forged header. No `api_secret_key`, access token, or privileged account for the *victim* shop is needed — only knowledge of the endpoint URL, which is typically public/predictable for embedded apps.

### Recommendation
Bind the tenant/shop identity into the signed material, not just headers that ride alongside it. Concretely:
- Include `shop` (and ideally `topic`/`webhook_id`) in `to_signable_string`, or otherwise validate them against server-side state that was itself established via an authenticated channel (e.g., verify the shop has a registered `Registry` entry created via an authenticated OAuth/session flow before dispatching).
- Document/enforce that consumers of `WebhookMetadata#shop` must correlate it against a previously verified session for that exact shop rather than trusting the header value outright.

### Proof of Concept
1. Install the app normally on `attacker-shop.myshopify.com`; trigger a webhook event so Shopify sends a legitimately signed request: body `B`, `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Capture `B` and `H` (the attacker fully controls their own inbound traffic/logs).
3. Replay the request to the same webhook endpoint, keeping `B` and `H` identical but setting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the signature purely from `B` and matches `H` — the request passes validation.
5. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` [4](#0-3) , causing the host app to process attacker-controlled payload `B` under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
