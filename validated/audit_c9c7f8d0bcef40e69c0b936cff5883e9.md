### Title
Webhook shop-domain identity binding not covered by HMAC signature - allows cross-tenant webhook spoofing (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface, and its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

The HMAC verification performed in `Registry.process` therefore only authenticates the JSON body bytes, not the accompanying headers: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` (the raw body only) and compares it to the `hmac` field: [3](#0-2) 

Meanwhile, `request.shop` — the field used to identify *which merchant/tenant* the webhook event belongs to — is read directly and unauthenticatedly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is **not** part of the signed payload: [4](#0-3) [5](#0-4) 

That unauthenticated `shop` value (along with `topic`, `api_version`, and `webhook_id`, also header-derived and unauthenticated) is passed straight into `WebhookMetadata` and handed to the host application's handler as trusted tenant-identifying data: [6](#0-5) 

**Identity binding broken (equality that should hold but doesn't):**
`shop (HMAC-authenticated) == shop (used to route/attribute the webhook event to a tenant)`

Because the HMAC only binds the body bytes, the `shop` value used to select which merchant's data pipeline processes the webhook is never checked against anything cryptographically bound to that shop. Any bytes claiming to be from `shop-A` with a body whose HMAC was legitimately computed by Shopify for `shop-B` (or vice versa, since the body content itself doesn't have to differ) will pass validation.

### Impact Explanation
An unprivileged internet user who can install any free/public app (i.e., become a legitimate, unprivileged tenant of the host application) can receive real, validly-HMAC-signed webhook deliveries for their **own** shop. Because the signature covers only the raw body and not the `shop-domain`, `topic`, `api_version`, or `webhook_id` headers, the attacker can capture one such valid `(body, hmac)` pair and replay it against the host application's webhook endpoint while substituting the `shop-domain` header with an arbitrary *other* merchant's domain. `Registry.process` will accept it as valid (the HMAC still matches the unchanged body) and dispatch it to the app's handler with `shop` set to the attacker-chosen value.

If the host application (as is standard/documented practice for this gem, e.g. in `webhook_handler.rb` usage) uses `WebhookMetadata#shop` to look up the tenant's stored `Session`/access token, update per-shop records, or otherwise scope tenant data, this results in cross-tenant data confusion: an attacker can inject fabricated events attributed to a victim shop, or cause the host app to process attacker-controlled body content (e.g. `orders/create`, `app/uninstalled`, `shop/redact`) under a false shop identity. This directly matches the "cross-tenant access" Critical-impact criterion, since the tenant boundary (`shop`) is not bound to the authenticated bytes.

### Likelihood Explanation
Reachable by any unprivileged internet user with no special access: obtaining a legitimate `(body, hmac)` pair only requires having a working installation of the target app on any shop they control (or observing any webhook delivery, since delivery endpoints are public HTTP(S) endpoints). Forging the header set and replaying the request requires no secret material (`api_secret_key`, access token) — only standard HTTP client capability. This is a straightforward, low-effort replay/spoof once one genuine webhook has been observed.

### Recommendation
Bind the tenant-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) into the signed material, or otherwise cryptographically verify them (e.g., require the caller to independently confirm the shop still has an active/matching session/webhook registration for the specific `webhook_id` before trusting `request.shop`), rather than trusting header values that fall outside the HMAC's scope. At minimum, document prominently that `Registry.process`'s HMAC check does not authenticate `shop`, `topic`, or `webhook_id`, and require host applications to independently validate the shop domain (e.g., against known/installed shops) before acting on webhook data.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (unprivileged/normal onboarding).
2. Shopify sends a legitimate webhook to the app's endpoint, e.g. body `{"id":123}"`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of body>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: orders/create`
3. Attacker captures this request, then replays it to the same endpoint, keeping `body` and `x-shopify-hmac-sha256` unchanged, but overwriting `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally other headers).
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` recomputes the HMAC solely from `@raw_body`, which is unchanged, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-supplied data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
