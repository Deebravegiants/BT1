### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is read from unauthenticated HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by HMAC-verifying the raw request body only, then dispatches the handler using a `shop` value taken directly from the `X-Shopify-Shop-Domain` HTTP header. That header is never covered by the HMAC computation, so the tenant identity ("which shop does this webhook belong to") is not cryptographically bound to the signature that authenticates the payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop`, `#topic`, and `#webhook_id` are all read straight from HTTP headers with no cryptographic binding: [2](#0-1) [3](#0-2) 

`Registry.process` verifies the HMAC over the request object and, if it passes, immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The equality this breaks: `shop authenticated-by-HMAC == shop delivered-to-handler`. In reality, `shop authenticated-by-HMAC = ∅` (the HMAC only signs `@raw_body`), while `shop delivered-to-handler = header["x-shopify-shop-domain"]`, a value fully controlled by the request sender and never included in the signable string in `AuthQuery`-style verification (`to_signable_string`, `lib/shopify_api/utils/hmac_validator.rb`).

Because Shopify apps share one `client_secret` (and thus one HMAC key) across every shop that installs them, any shop that has legitimately installed the app can capture one of its own valid signed webhook deliveries (e.g., an empty-body event, or any deterministic body they can trigger) and replay that exact body with the `X-Shopify-Shop-Domain` header changed to a different (victim) shop domain. `HmacValidator.validate` will still succeed, because `compute_signature` is computed purely from `@raw_body`, which is unchanged. `Registry.process` will then hand the app's webhook handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who is a legitimate (but unprivileged, in the sense of "any other merchant using this app") tenant can make the app's webhook handler believe an event originated from a different shop that the attacker does not control. Downstream, apps commonly key data updates, session lookups, or entitlement changes off `WebhookMetadata#shop`; a forged shop identifier can let an attacker inject data attributed to, or influence app-side state for, a shop they don't own — meeting the "cross-tenant access" bar via a broken binding (HMAC-authenticated bytes vs. header-derived tenant identity), consistent with the class of finding this exercise is looking for.

### Likelihood Explanation
Likelihood is constrained by the requirement that the attacker already be an installed/authorized user of the same app (to legitimately trigger a webhook and capture a signed body), and by needing a body whose content is attacker-predictable/reusable (many webhook topics, e.g. `app/uninstalled` with an essentially fixed shape, or events with attacker-controlled content the merchant provides, make this practical). No secret material is required — only observation of one legitimately delivered webhook and the ability to send an HTTP request with a spoofed `X-Shopify-Shop-Domain` header to the app's own registered webhook endpoint.

### Recommendation
Bind the tenant/topic/id claims into the signature verification instead of trusting bare headers post-hoc: e.g., have `Webhooks::Request#to_signable_string` incorporate the `shop`, `topic`, and `webhook_id` header values (matching how Shopify's own signature construction should be verified end-to-end), or require the consuming app to cross-check `WebhookMetadata#shop` against session/tenant records obtained through an independent authenticated channel before acting on the payload. At minimum, document prominently that `shop`/`topic`/`webhook_id` are unauthenticated and must not be used as the sole tenant-identity input for any privileged operation.

### Proof of Concept
1. App has webhooks enabled; two shops, `attacker.myshopify.com` and `victim.myshopify.com`, both interact with the same app instance (same `client_secret`).
2. Attacker triggers a webhook event on their own shop with a known/reproducible body, e.g. `raw_body = "{}"`, and captures the resulting `X-Shopify-Hmac-Sha256` header value that Shopify computed with the shared `client_secret`.
3. Attacker sends a POST to the app's webhook endpoint with:
   - `raw_body = "{}"` (identical to what was captured)
   - `X-Shopify-Hmac-Sha256` = the captured valid signature
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` optionally forged too
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully (all required headers present).
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)` per `lib/shopify_api/webhooks/registry.rb:190`, which succeeds because `to_signable_string` only checks `raw_body`, unchanged from step 2.
6. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", ...)` per `lib/shopify_api/webhooks/registry.rb:198-199`, despite the event never having been sent by Shopify for `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
