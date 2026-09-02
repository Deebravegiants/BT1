### Title
Webhook `shop` Identity Not Bound to HMAC Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw body only, while the `shop` value used to route the webhook to a tenant's handler is read from an unauthenticated header. An attacker who can obtain any single genuine, validly-signed webhook payload (e.g., by installing the public app on their own store) can replay that exact body with a forged `shopify-shop-domain` header pointing at a victim shop, and the gem's HMAC check will still pass.

### Finding Description
`Webhooks::Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signed material: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate`, which internally calls `to_signable_string` (body only) and compares it against the HMAC computed with the shared `api_secret_key`: [3](#0-2) 

If validation succeeds, `Registry.process` immediately forwards `request.shop` — the unauthenticated header value — to the app-supplied handler as the tenant identity for the event, with no cross-check against the body contents: [4](#0-3) [5](#0-4) 

**Broken binding:** `shop header value == shop that produced/authorized the signed body`. Before the attacker's action, this equality holds because Shopify itself sets the header alongside a body it generated for that same shop. After the attacker's action, the equality is broken: the body (and its valid HMAC) originates from the attacker's own shop, but the `shop` field consumed by the app is swapped to an arbitrary victim's domain, while the HMAC still validates because it never covered `shop` in the first place.

Since `api_secret_key` is shared across every shop that installs a given public app, any unprivileged user can:
1. Install the target app on their own (attacker-controlled) Shopify development/trial store — no privileged credentials required.
2. Capture one legitimate webhook delivery (topic, raw body, and its valid `X-Shopify-Hmac-Sha256`) that Shopify sends to the app for that store.
3. Replay the identical body/HMAC pair to the app's webhook endpoint, substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` passes (it only checks the body), and `Registry.process` hands the handler a `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` with attacker-chosen body content.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem cannot distinguish a genuine webhook about shop A from an attacker-forged webhook that merely claims to be about shop A. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up the tenant record and merge in `body` data, or to satisfy mandatory compliance topics like `shop/redact`/`customers/redact`), this permits cross-tenant data injection/corruption or fabricated compliance events attributed to a shop that never triggered them — classified as Critical cross-tenant access per the scope's impact list.

### Likelihood Explanation
Exploitation only requires the ability to install the same public app on an attacker-controlled store (an ordinary, unprivileged action available to anyone) and standard HTTP request forgery to replay a captured payload with a modified header. No access to `api_secret_key`, tokens, or victim credentials is needed, making this practically reachable by any internet user targeting an app that hosts this gem's webhook processing.

### Recommendation
Bind the `shop` (and ideally `topic`, `api-version`, `webhook-id`) values into the signed material, or otherwise cryptographically tie the header-derived identity to the payload before trusting it. At minimum, `to_signable_string` should incorporate the `shop`, `topic`, and other trust-sensitive headers so the HMAC check fails if any of them are altered relative to what Shopify originally signed for, e.g.:
```diff
 def to_signable_string
-  @raw_body
+  "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
 end
```
(with Shopify's HMAC generation updated accordingly, or by validating shop/topic out-of-band against a per-install allow-list before dispatching to handlers).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (public app install, unprivileged).
2. Shopify sends a legitimate webhook, e.g. `orders/create`, to the app's endpoint with headers:
   - `X-Shopify-Hmac-Sha256: <valid-hmac-for-body>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - body: `{"id": 1, "total_price": "0.01", ...}`
3. Attacker captures the raw body and the exact `X-Shopify-Hmac-Sha256` value.
4. Attacker replays the same body and HMAC to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` builds the `Request`, calls `Utils::HmacValidator.validate(request)` — this passes because it only hashes `@raw_body`, per [1](#0-0)  and [6](#0-5) .
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)` and processes it as if it were a genuine event for the victim tenant, per [7](#0-6) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
