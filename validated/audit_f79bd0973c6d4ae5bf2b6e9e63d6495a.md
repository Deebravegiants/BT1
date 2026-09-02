### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to route and label the payload come from HTTP headers that are excluded from that signature. This breaks the identity binding `hmac(body) == hmac(body)` versus what is actually acted upon, `shop_header != verified_field`, letting any holder of one genuine `(body, hmac)` pair relabel it as coming from an arbitrary shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read straight from attacker-controllable headers with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the body) against the HMAC: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` to the app's handler as if they were verified: [4](#0-3) 

Because Shopify's webhook HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app rather than being shop-specific, a merchant who installs the app can legitimately receive real `(body, hmac)` pairs for their own shop's events. Since the header fields are outside the signed content, that same person can resubmit the identical body/HMAC to the app's webhook endpoint while swapping `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) to name a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspected those headers, and `WebhookMetadata.shop` is populated with the forged value: [5](#0-4) 

This is the exact class of bug flagged in the report: a value the caller acts on (`shop`) is not covered by the integrity check that gates execution, breaking the intended equality `verified_bytes == acted_upon_bytes`.

By contrast, the OAuth callback path (`AuthQuery`) does bind `shop` into the signed content, so it is not vulnerable to this analog: [6](#0-5) 

### Impact Explanation
Any downstream application that keys per-tenant logic (order/customer records, billing, GDPR redaction, credential lookups, etc.) off `WebhookMetadata#shop` — the field this gem explicitly hands the handler as the webhook's shop — can be made to act on a different shop's tenant than the one that actually produced the signed payload. This is a cross-tenant identity confusion introduced by the gem's own `Request`/`Registry` design, not merely host misuse of an undocumented field, since `shop` is the gem's documented accessor for "the shop the webhook belongs to."

### Likelihood Explanation
Exploitation requires only: (1) being a merchant who has installed the target app (an unprivileged position relative to other tenants) so as to receive at least one genuine webhook body/HMAC pair, and (2) resending that body with a rewritten `shop-domain` header to the app's public webhook endpoint. No secret material, TLS interception, or social engineering is required — only normal use of the app as an installed merchant.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the HMAC-signable content for webhook requests, or otherwise cryptographically bind the header-derived identity to the signed body before exposing it via `WebhookMetadata`. Alternatively, document loudly that `Request#shop`/`#topic`/`#webhook_id` are unauthenticated and must not be trusted for tenant-scoping decisions without independent verification (e.g., cross-checking against the shop domain in the parsed body where Shopify includes one).

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker owns/controls this store and can receive real webhooks for it.
2. Shopify sends a legitimate webhook: headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw body>`, some `raw_body`.
3. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only (`Request#to_signable_string`) and it matches, so `Registry.process` proceeds.
5. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` and performs whatever tenant-scoped action the app implements for that shop, using attacker-supplied body content mislabeled as victim data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
