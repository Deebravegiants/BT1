Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  — the `topic`, `shop`, `api-version`, and `webhook-id` headers are read straight from unauthenticated HTTP headers and are never part of the HMAC-signed material [2](#0-1) . `Registry.process` validates only the body's HMAC and then dispatches using the unauthenticated `shop` header value [3](#0-2) .

### Title
Webhook `shop` (and `topic`) identity fields are unauthenticated / not covered by HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC in `x-shopify-hmac-sha256` authenticates *only the JSON payload bytes*, never the `shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, or `shopify-webhook-id` headers. `Registry.process` treats `request.shop` and `request.topic` as trusted tenant/routing identifiers passed straight into `WebhookMetadata` and the registered handler, despite these values never being bound to the signature.

### Finding Description
`HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method is hard-coded to `@raw_body` [1](#0-0) . Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are plain header reads with no cryptographic binding to the HMAC [2](#0-1) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body-only validation) and then uses `request.shop`/`request.topic` unquestioningly to select the handler and build `WebhookMetadata` that is handed to app code as the trusted tenant identity [3](#0-2) .

Since Shopify apps share a single `client_secret` across every shop that installs them, any shop owner who installs the app (an ordinary, unprivileged merchant relative to *other* merchants using the same app) can receive genuinely-signed webhooks for their own store. Because the signature covers only the body — not the `shop-domain` header — that same attacker can capture one of their own validly-signed webhook deliveries and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop. `Utils::HmacValidator.validate` will still pass (the body bytes are unchanged and the secret is shared), yet `Registry.process` will hand the app's handler a `WebhookMetadata` claiming the data belongs to the victim shop.

This breaks the equality the gem is implicitly supposed to enforce: `shop authenticated (bound by HMAC) == shop acted upon (used for tenant routing)`. In this gem, the left side is empty (no shop binding at all) while the right side is the attacker-controlled header.

### Impact Explanation
An app that trusts `WebhookMetadata#shop`/`#topic` (as `ShopifyAPI::Webhooks::Registry` is explicitly designed for callers to do — that's the entire purpose of `Request#shop`) to select which tenant's records to create/update/delete can be tricked into attributing attacker-supplied webhook content to a different, victim shop. This is a cross-tenant data-integrity breach: an unprivileged merchant can make the host application process fabricated events (e.g., order/customer data changes, `customers/redact`, `shop/redact`) under another merchant's identity, without ever needing that merchant's access token or credentials.

### Likelihood Explanation
Any merchant who installs the app already automatically receives correctly-signed webhook deliveries for their own shop from Shopify. Capturing one's own webhook body (via a local proxy/logging endpoint they control, or simply their own app's request logs) and replaying it with a modified `shop-domain` header requires no secret material and no privileged access — only the ability to send an arbitrary HTTP POST to the app's public webhook endpoint, which is by definition internet-reachable.

### Recommendation
Bind the `shop` (and ideally `topic`) values into the signed material, or independently verify that the shop in the header corresponds to a shop with an active session/installation known to the app before trusting it for tenant-scoped operations. At minimum, document that `Webhooks::Request#shop`/`#topic` are unauthenticated and must not be used for tenant identification without additional verification (e.g. cross-checking against `Auth::Session` records keyed by shop).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, giving them a legitimate, signed webhook delivery from Shopify for a topic like `customers/create`:
```
POST /webhooks HTTP/1.1
x-shopify-topic: customers/create
x-shopify-hmac-sha256: <valid HMAC over body>
x-shopify-shop-domain: attacker.myshopify.com
x-shopify-webhook-id: ...
Body: {"id": 1, "email": "attacker@example.com", ...}
```
2. Attacker replays the exact same request to the app's webhook endpoint, only changing the `x-shopify-shop-domain` header to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes the HMAC over the unchanged body with the shared `client_secret` and it matches — validation passes [4](#0-3) .
4. `Registry.process` dispatches `WebhookMetadata.new(topic: "customers/create", shop: "victim.myshopify.com", body: {...attacker-controlled...}, ...)` to the registered handler [5](#0-4) , causing the host app to act on forged data attributed to the victim's shop.

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
