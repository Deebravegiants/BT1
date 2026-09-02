### Title
Webhook shop identity spoofing via HMAC-excluded `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to app webhook handlers from an HTTP header that is **not** covered by the webhook's HMAC signature, so the value that gets HMAC-verified (`raw_body`) is not the same value that identifies which shop the webhook is attributed to. This breaks the intended binding `hmac_signed_bytes == identity_bytes acted upon`.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` verifies the `Request` by recomputing the HMAC over `to_signable_string` and comparing it to the `hmac` header value: [1](#0-0) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns **only the raw body**: [2](#0-1) 

But the `shop` accessor — the value used to identify which merchant/tenant the webhook belongs to — is read straight from an HTTP header (`x-shopify-shop-domain` / `shopify-shop-domain`) that is never included in the signed content: [3](#0-2) 

`Registry.process` only validates the HMAC of the body before dispatching to the handler with `request.shop` taken from the unsigned header: [4](#0-3) 

Because Shopify signs webhooks with the **app's** `api_secret_key` (shared across every shop that installs the app), not a per-shop secret, any valid `(raw_body, hmac)` pair obtained from a legitimate webhook delivered to the app (e.g., by installing the app on an attacker-controlled test store, or intercepting/replaying any webhook) remains HMAC-valid regardless of which shop domain is attached, since `shop-domain` is excluded from `to_signable_string`. An attacker can therefore take a genuine, correctly-signed webhook body/HMAC pair and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The signature check in `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` forwards `shop: request.shop` (attacker-controlled victim domain) to the handler as if the payload genuinely originated from that victim shop.

This equality that should hold is:
`bytes covered by HMAC == bytes used to bind the payload to a tenant`
but instead:
`bytes covered by HMAC (body only) != tenant-identifying bytes (shop-domain header, unsigned)`

### Impact Explanation
This allows cross-tenant confusion/spoofing: a handler that trusts `WebhookMetadata#shop` (built directly from the unverified header) to select which shop's session/data to update can be tricked into applying attacker-controlled webhook payload content under a victim shop's identity. Any app built on this gem that relies on `Registry.process`'s webhook `shop` field for tenant-scoped side effects (data updates, cache invalidation, redaction/compliance actions, etc.) is exposed to cross-tenant data confusion — matching the "Critical – cross-tenant access" impact category, since the shop binding that should be authenticated is not actually authenticated by the HMAC.

### Likelihood Explanation
Medium-High: the attacker needs one legitimately-signed `(body, hmac)` pair for the target app, which is trivial to obtain — install the app on an attacker-owned development/trial store (a normal, unprivileged action) and capture any webhook delivery, or otherwise obtain any prior legitimate delivery. No access token, `client_secret`, or privileged account is required; the `api_secret_key` is never exposed to the attacker, only reused via replay with a modified header.

### Recommendation
Include the shop domain (and other identity-relevant headers such as topic/api-version) in the HMAC-covered signable content, or independently bind `request.shop` to a value that is cryptographically tied to the signature (e.g., verify the shop against the session/webhook subscription that was registered, not solely a raw header echoed back by the caller). At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant-scoping decisions without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, triggers a webhook (e.g., `app/uninstalled` or any topic with a fixed/predictable body such as `{}`), and captures the resulting `raw_body` and `x-shopify-hmac-sha256` value — both are valid because they were genuinely signed by Shopify with the app's `api_secret_key`.
2. Attacker POSTs to the app's webhook endpoint reusing that exact `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body as usual; `Utils::HmacValidator.validate(request)` recomputes HMAC over `to_signable_string` (`raw_body` only) and it matches, since `shop-domain` was never part of the signed content [2](#0-1) .
4. `Registry.process` dispatches to the handler with `shop: request.shop` = `"victim-shop.myshopify.com"` [4](#0-3) , even though the payload actually originated from the attacker's own shop and was never authenticated as belonging to the victim.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
