### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor sourced directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator.validate` is computed only over the raw request body (`to_signable_string` returns `@raw_body`). The `shop` header value is never included in the signed material, so the tenant identity delivered to webhook handlers is not bound to the cryptographic proof of authenticity.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by calling `Utils::HmacValidator.validate(request)`, which only checks the HMAC over `request.to_signable_string`: [1](#0-0) 

`Request#to_signable_string` returns solely the raw body bytes: [2](#0-1) 

But `Request#shop` (used to populate `WebhookMetadata#shop`, which is handed to the app's `WebhookHandler#handle`) is read straight from the `shop-domain` header, with no cryptographic tie to the signed body: [3](#0-2) [4](#0-3) 

The binding the library implicitly claims to provide is:
`hmac_valid(body) == true` implies `shop_header == originating_shop_of(body)`.

That equality does not hold: `hmac_valid` proves only that *some* request bearing this body was signed with the app's secret at some point — it says nothing about which shop header accompanies it. Since a single Shopify app's `client_secret`/`api_secret_key` is shared across every shop that installs it, any attacker who installs the app on their own (free, self-controlled) development shop can trigger a webhook event, capture the genuinely-signed `raw_body` + `hmac-sha256` value Shopify sent them, and then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header (e.g., a victim's shop). `HmacValidator.validate` will report success because it never inspects the header, and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain and `body` containing attacker-controlled data signed under the attacker's own legitimate webhook.

Because host applications are documented and expected to key their per-tenant records off `WebhookMetadata#shop` (this is the only tenant identifier the gem exposes to the handler), this breaks the shop-authenticated-vs-shop-used-as-key binding described in the rules: the shop that was actually cryptographically authenticated (via body HMAC tied to the attacker's own shop-originated event) diverges from the shop value the handler is told to act on.

### Impact Explanation
This allows cross-tenant data injection/corruption: an unprivileged attacker (anyone who can install the app on their own store, which is normal, unprivileged app-install behavior, not a "privileged account") can make the app process forged webhook payloads under a victim shop's identity. Depending on how the host app is documented to use `WebhookMetadata#shop` (as the tenant key for orders/customers/inventory updates, GDPR data-request routing, etc.), this can lead to cross-tenant access/writes purely through this gem's own header-vs-signature mismatch — matching the "Critical: cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is elevated because the attacker does not need to compromise any secret or session: they only need their own installation of the target app (a normal, unauthenticated capability for any Shopify merchant/developer) to produce a genuinely-signed body/HMAC pair, then a trivial HTTP replay with a modified header to the app's public webhook endpoint. No leaked credentials, TLS interception, or privileged account is required — only the ordinary ability to install the app once as any shop.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically tie the header values to the payload before trusting them:
- Include the `shop-domain` header (and other identity-bearing headers) in `to_signable_string` so `Utils::HmacValidator.validate` fails if any of them are altered, or
- Cross-check `request.shop` against an out-of-band trusted value (e.g., look up the webhook subscription/shop mapping by `webhook_id` returned from Shopify's Admin API) before dispatching to the handler, rather than trusting the raw header as the tenant identity.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (normal, unauthenticated install flow).
2. Attacker triggers a real event (e.g., `orders/create`) in their own store, causing Shopify to send a webhook to the app's endpoint with:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over raw_body computed with the app's shared api_secret_key>`
   - `raw_body: <attacker-controlled order JSON, since attacker controls the content of orders in their own store>`
3. Attacker replays this exact `raw_body` + `hmac-sha256` value to the app's webhook endpoint again, but this time sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this succeeds because the HMAC only covers `raw_body`, which is unchanged from step 2. [1](#0-0) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
