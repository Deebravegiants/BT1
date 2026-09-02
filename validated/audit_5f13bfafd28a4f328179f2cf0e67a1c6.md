### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable content solely from the raw request body, while the `shop` value that downstream handlers trust to identify the tenant is read from an unauthenticated header. This breaks the intended binding `hmac == HMAC(secret, body ‖ shop)` down to `hmac == HMAC(secret, body)`, letting an attacker who possesses any valid `(body, hmac)` pair replay it with an arbitrary `shop` value.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) . `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic tie to the HMAC: [2](#0-1) .

`Utils::HmacValidator.validate` verifies the received HMAC exclusively against `to_signable_string` (i.e., the body), never incorporating the shop header: [3](#0-2) .

`Registry.process` trusts `request.shop` after only this HMAC check passes, and forwards it as the tenant identity to the app's webhook handler: [4](#0-3) . The `WebhookMetadata` struct passed to handlers exposes `shop` as an authoritative field: [5](#0-4) .

Because a Shopify app's `client_secret` (`api_secret_key`) is shared across every shop that installs the app — it is not shop-specific — any merchant who legitimately installs the app can trigger real webhook deliveries for their own store and thereby obtain valid `(raw_body, hmac)` pairs signed with the app's shared secret. Since the shop identity is not part of the signed content, that attacker can send the same body and HMAC directly to the app's public webhook endpoint while forging the `X-Shopify-Shop-Domain` header to name a different (victim) shop. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop.

This is precisely the class of bug in the report: a field that is acted upon (`shop`, used to select/attribute the tenant) is not covered by the integrity check (`hmac` only covers `body`), so the two identities the code treats as equal — "the shop whose webhook is being delivered" and "the shop that authenticated via HMAC" — silently diverge under attacker control.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` to determine which merchant record to update, delete, or act upon (the documented and expected usage pattern for `WebhookHandler#handle`), an attacker can cause the app to process attacker-supplied webhook content under a victim shop's identity. This is a cross-tenant confusion: a merchant with no privileges on the victim's store can inject events attributed to that store (e.g., triggering `shop/redact`/`customers/redact`-style processing, uninstall handling, or app-specific reactive logic) purely by forging the shop header on a request carrying a body+HMAC pair they legitimately obtained from their own installation. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker needs only to: (1) install the app on a shop they control (or otherwise cause the app to deliver a webhook to them), (2) capture the raw body and `X-Shopify-Hmac-SHA256` header of a real delivery, and (3) POST that same body/HMAC to the app's public webhook endpoint with a spoofed `X-Shopify-Shop-Domain` header. No access token, `client_secret`, or privileged account is required — only the ability to install the app as an ordinary unprivileged merchant, which is the normal, unauthenticated app-installation path. Likelihood is High.

### Recommendation
Bind the shop identity into the signed material actually verified, or otherwise cryptographically tie `request.shop` to the HMAC-covered content rather than trusting it from an independent header. Options:
- Extend `to_signable_string` to include the shop domain (if Shopify's webhook HMAC scheme is updated to support this) or
- Cross-check `request.shop` against an independently trusted source (e.g., look up the webhook subscription/shop the payload's own body claims to belong to and refuse mismatches), or
- Document explicitly and enforce in `Registry.process` that `data.shop` must never be used by host apps as the sole tenant identifier for privileged actions without an additional binding (e.g., re-deriving shop from Shopify's registered callback address per shop, or requiring mutual TLS/IP allow-listing for the webhook endpoint).
At minimum, update `HmacValidator`/`Request` so any field used for tenant attribution is included in `to_signable_string`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they own) via the normal OAuth flow — no special privilege needed.
2. Attacker triggers any subscribed webhook topic (e.g., updates an order) causing Shopify to POST a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-SHA256: H`, where `H = HMAC_SHA256(client_secret, B)`.
3. Attacker captures `(B, H)`.
4. Attacker sends their own POST directly to the app's public webhook URL:
```
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-SHA256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: <any>
X-Shopify-Api-Version: 2024-01

B
```
5. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `shop` returns `victim-shop.myshopify.com` [2](#0-1) .
6. `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)`, which equals `H`, so validation succeeds [6](#0-5) .
7. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body(B), ...)` [7](#0-6) , causing the app to process attacker-controlled webhook data as if it belongs to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
