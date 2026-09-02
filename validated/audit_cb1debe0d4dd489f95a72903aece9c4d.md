### Title
Webhook HMAC only covers the request body, not the `shop-domain` header — cross-tenant webhook identity spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's HMAC before dispatching it to the app's handler, and the documentation explicitly states this "will verify the request did indeed come from Shopify" before the handler is called with a `WebhookMetadata` object exposing `shop`. However, the HMAC signature only binds the raw body — it does not bind the `shop-domain`, `topic`, or `webhook-id` headers. Because a single app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, this breaks the intended identity binding: `shop header value == tenant that produced the signed body`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely from `to_signable_string`, i.e. the body only, and never incorporates `shop`, `topic`, or `webhook_id`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as sufficient proof of authenticity for the *entire* request, then forwards the unauthenticated `request.shop` header straight into the handler: [3](#0-2) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or HMAC: [4](#0-3) 

Because the app's `client_secret` (used as `Context.api_secret_key`) is the same for every shop that installs the app (it is a per-app secret, not a per-shop secret), an attacker who controls one legitimate installation of the app can:
1. Install the app on their own (attacker-controlled) shop and trigger Shopify to deliver a real webhook — Shopify signs the body with the app's shared secret and sets `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Capture that valid `(raw_body, hmac)` pair.
3. Replay the exact same body/HMAC to the app's webhook endpoint, but substitute `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` still succeeds (it only checks the body against the shared secret), and `Registry.process` calls the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the body content actually originated from the attacker's own shop.

The library presents `data.shop` to the handler as a value that has passed webhook verification ("This will verify the request did indeed come from Shopify"), per the documentation at `docs/usage/webhooks.md` lines 125-135, but that guarantee does not actually extend to the `shop` field.

### Impact Explanation
This is a cross-tenant identity-binding break: the equality that should hold is `verified_hmac_body ⇔ shop_header`, but the gem only enforces `verified_hmac ⇔ body`. Any downstream logic that uses `data.shop` to select the tenant context (e.g., looking up that shop's session/access token to act on the webhook, writing the payload into a shop-scoped record, or triggering shop-specific business logic) will apply attacker-controlled body content under a victim shop's identity. This satisfies the Critical bar of "cross-tenant access" because the trust boundary broken here is the gem's own webhook-verification API contract — the host app is not required to do anything unusual; it is simply relying on `Registry.process`'s documented guarantee and the `WebhookMetadata.shop` field it returns.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on any shop they control (a standard, unprivileged action for any Shopify merchant/developer) and capture one real webhook delivery for a topic the app has registered — no access to `api_secret_key`, no privileged account, and no TLS interception is required. Replaying an HTTP POST with a modified header while keeping the byte-identical body and HMAC is trivial.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook_id`, `api_version`) headers in the HMAC-signable string, or otherwise cryptographically bind them to the payload before trusting `request.shop` in `Registry.process`. At minimum, the gem should document that `WebhookMetadata.shop` is not covered by the HMAC and must not be used as an authoritative tenant identifier without additional verification (e.g., cross-checking against a known/registered shop for that webhook subscription).

### Proof of Concept
1. Install the target Shopify app on `attacker-shop.myshopify.com`.
2. Trigger a webhook event (e.g., `orders/create`) with attacker-controlled order content; Shopify delivers:
   ```
   POST /callback/orders/create
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over raw_body, using the app's shared client_secret>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "malicious payload"}
   ```
3. Replay this exact request to the same endpoint, changing only:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
   (body and `X-Shopify-Hmac-Sha256` unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only validates `raw_body`.
5. The registered handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and `body == {"id": 1, "note": "malicious payload"}` — attacker-controlled data processed under the victim shop's tenant identity.

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
