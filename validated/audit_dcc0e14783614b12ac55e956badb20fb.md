### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values come from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` treats HMAC success as proof the whole request "did indeed come from Shopify" and forwards the header-derived `shop` straight to the app's handler. Because the same app-level `api_secret_key` signs webhooks for every shop that has installed the app, an unprivileged attacker who installs the app on their own store can capture a validly-signed `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop. The HMAC check still passes, and the app receives a webhook it believes belongs to the victim tenant.

### Finding Description
The identity binding that should hold is:
`hmac == HMAC(secret, bytes_that_include_shop)` but instead the gem enforces only
`hmac == HMAC(secret, raw_body)`.

- `to_signable_string` for webhook requests returns only the raw body: [1](#0-0) 
- `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from attacker-controllable HTTP headers, none of which participate in the signature: [2](#0-1) 
- `Registry.process` validates only the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the handler: [3](#0-2) 
- The documentation explicitly tells developers that calling `Registry.process` "will verify the request did indeed come from Shopify," and shows the canonical handler pattern trusting `data.shop` directly: `docs/usage/webhooks.md` lines 10-30, 125.

Because webhooks for every shop that installs an app are signed with the same `api_secret_key` (there is no per-shop signing key involved from the gem's perspective), any shop owner — an ordinary, unprivileged Shopify merchant/attacker who installs the target app on their own store — can obtain a genuinely valid `(body, hmac)` pair from a webhook Shopify sends them. Since `shop` is excluded from the signed content, that same `(body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a different, victim shop domain. `HmacValidator.validate` succeeds under `lib/shopify_api/utils/hmac_validator.rb` because it never inspects `shop`, and `Registry.process` dispatches the forged `shop` to the host app's handler as authenticated tenant data.

### Impact Explanation
This breaks the shop-authenticated-versus-shop-acted-upon binding across a tenant boundary, matching the report's underlying bug class ("a field acted on but not covered by the HMAC"). A host application following the gem's own documented handler pattern (using `data.shop` to key persistence, deletion, redaction, or session-invalidation logic for topics such as `app/uninstalled`, `shop/update`, `customers/redact`, `shop/redact`) can be tricked into applying webhook-triggered state changes to the wrong tenant's records, i.e., cross-tenant access/impact, with no elevated privileges required by the attacker.

### Likelihood Explanation
Any developer account can install a target app on a free/trial store to obtain a validly signed webhook without needing the app's `api_secret_key`, an access token, or any leaked credential — only normal installation flow is required. Capturing and replaying the body+HMAC while altering only the shop-domain header is straightforward given the gem's documented processing flow.

### Recommendation
Bind the tenant identity to the signature: include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the bytes that are HMAC-verified, e.g. change `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to combine the shop-domain header with the raw body (mirroring how Shopify webhooks should be verified), or validate that any shop identifier embedded in the parsed payload matches the header before trusting `request.shop`, and update the documentation/`WebhookMetadata` contract so `shop` is only asserted once cryptographically bound.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged installation).
2. Shopify sends a legitimate webhook, e.g. `app/uninstalled`, to the app's callback URL with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - body: `{"id":..., "domain":"attacker-shop.myshopify.com", ...}` (or a topic with a generic/empty body)
3. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value.
4. Attacker sends a new POST to the app's webhook endpoint using the same `raw_body` and same `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` matches (`lib/shopify_api/webhooks/request.rb` lines 10-13), and `Utils::HmacValidator.validate` succeeds because it only hashes `raw_body` (`lib/shopify_api/utils/hmac_validator.rb` lines 26-31, `lib/shopify_api/webhooks/request.rb` lines 35-38).
6. `ShopifyAPI::Webhooks::Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-199), causing the host application to act on `victim-shop` using attacker-supplied/attacker-timed webhook content.

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
