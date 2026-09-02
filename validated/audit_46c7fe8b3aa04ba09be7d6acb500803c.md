Confirmed: the `shop`, `topic`, `api_version`, and `webhook_id` fields consumed by `Registry.process` and delivered to app handlers via `WebhookMetadata` are read straight from HTTP headers [1](#0-0)  while the only bytes covered by the HMAC signature are the raw body [2](#0-1) , and `HmacValidator` verifies exactly that signable string against the received signature [3](#0-2) , with `Registry.process` then trusting `request.shop`/`request.topic` post-validation to route to the tenant-specific handler [4](#0-3) .

### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `Utils::HmacValidator.validate` authenticates the body bytes but not the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers. `Registry.process` nonetheless uses these unauthenticated headers to select the handler and to populate `WebhookMetadata#shop`, which host applications use to attribute the event to a specific merchant/tenant. Anyone who can produce (or replay) one validly-signed webhook body — trivially obtainable by installing the target app on their own store, since the HMAC secret is the app-level `api_secret_key` shared across all merchants, not a per-shop secret — can resend that exact `(body, hmac)` pair to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header. `Utils::HmacValidator.validate` will still return `true` because it never inspects the shop header, and the handler will process the event as if it originated from the spoofed shop.

### Finding Description
- `AuthQuery`/`Request` both implement `Utils::VerifiableQuery`, whose contract is "sign whatever `to_signable_string` returns." For webhooks, `to_signable_string` is defined as just `@raw_body` [2](#0-1) .
- `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from HTTP headers with no cryptographic binding to the body or to each other [1](#0-0) .
- `HmacValidator.validate_signature` computes `HMAC(secret, to_signable_string)` and compares to the `hmac-sha256` header value using `OpenSSL.secure_compare` [3](#0-2) . Since `to_signable_string` never includes the shop header, a signature is valid for *any* shop header value paired with a given body.
- `Registry.process` raises only if the HMAC check fails, then immediately trusts `request.shop`/`request.topic` to dispatch to the registered handler and build `WebhookMetadata`, which is the object host apps key their per-shop business logic on [4](#0-3) [5](#0-4) .

This is the same identity-binding break pattern as the referenced report: the value that downstream logic *acts on* (there, the `from` address debited; here, the `shop` a webhook event is attributed to) is not the value that was *cryptographically verified* (there, nothing was verified at all; here, only the body was verified, not the shop). The equality that should hold — "the shop the signature was computed for == the shop the handler executes for" — does not hold, because the shop is outside the signed byte range entirely.

### Impact Explanation
An attacker who legitimately installs the vulnerable app on their own shop receives real, validly-HMAC-signed webhook deliveries for that shop (this requires no privileged credentials, no access token, and no knowledge of `api_secret_key`, since the secret is app-wide and the attacker only needs to observe traffic to their own owned endpoint). By replaying that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop, they can make the host application process arbitrary webhook events (e.g. `app/uninstalled`, `shop/redact`, `orders/create`, `customers/data_request`) as if they came from the victim shop. Depending on how the host app's registered `WebhookHandler#handle` implementation uses `WebhookMetadata#shop`, this enables cross-tenant data corruption, forged deauthorization/uninstall events, or injection of fabricated order/customer records attributed to another merchant — a cross-tenant boundary violation.

### Likelihood Explanation
High: no special access is required beyond installing the app once as an ordinary merchant (something any internet user can do for a public app), and replaying a captured HTTP request with one modified header is trivial. The vulnerable code path (`Registry.process` → `HmacValidator.validate` → handler dispatch) is the only verification step the gem provides, and it silently omits the shop/topic headers from the signed content.

### Recommendation
Bind the tenant-identifying headers into the signed/verified content, or otherwise cryptographically tie the shop to the verification step, e.g.:
- Include `shop-domain` (and ideally `topic`, `webhook-id`) in `Request#to_signable_string` if Shopify's delivery signature is computed over headers as well as body (verify against Shopify's current webhook signing spec), or
- Require the host application to cross-check `request.shop` against a shop that is already known/authorized (e.g. has an active session/access token) for this app installation before invoking the handler, rather than trusting the header outright.
At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be validated by the host app against its own shop/session store before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a real event (e.g. updates an order) so Shopify delivers a genuine webhook to the app's endpoint with body `B`, and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC_SHA256(api_secret_key, B)`.
2. Attacker captures this raw request (e.g., via a proxy in front of their own endpoint, or by running a copy of the same app themselves).
3. Attacker resends the identical request to the app's public webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(api_secret_key, B)` and compares it to `H` — this still matches because the shop header was never part of the signed input [2](#0-1) [3](#0-2) .
5. Validation succeeds; `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and invokes the app's handler as though the event genuinely originated from `victim-shop.myshopify.com` [4](#0-3) .

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
