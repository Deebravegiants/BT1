### Title
Webhook `shop` (and topic/api-version/webhook-id) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from HTTP headers, but `Utils::HmacValidator.validate` only authenticates the raw request **body**, not these headers. Any party who can obtain one valid `(body, hmac)` pair for a webhook (e.g. from their own shop where the app is installed) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The signature still verifies because the header is outside the signed content, so the app's webhook handler will process attacker-controlled data attributed to a shop the attacker does not own.

### Finding Description
The `hmac_validator` computes/verifies the signature purely from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw JSON body — none of the Shopify-supplied headers are part of the signed content: [2](#0-1) 

Yet `shop` (along with `topic`, `api_version`, `webhook_id`) — all sourced straight from headers — is what `Registry.process` hands to the app's business logic as the tenant identity for this webhook, right after HMAC validation passes: [3](#0-2) 

This breaks the intended identity binding: `hmac == HMAC(secret, body)` says nothing about `shop == body's actual originating shop`. The equality that should hold — "the shop-domain claimed by the request equals the shop bound to this signed payload" — is not enforced anywhere in this gem's webhook path.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who has legitimate access to a shop with the app installed (or who otherwise observes one valid webhook body+HMAC, e.g. an "identical" body across shops, like `orders/create` test payload shape, or any webhook whose JSON body happens to match across tenants) can re-send that same body/HMAC to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop. Since the gem's own validation logic (`HmacValidator.validate` + `Registry.process`) never checks that the header-derived `shop` is part of what was signed, the forged request is accepted as authentic and dispatched to the handler as if it originated from the victim shop. Any app relying on this gem's built-in `shop` field to scope handler logic (updating merchant data, triggering per-tenant workflows, billing, etc.) is exposed to cross-tenant data injection/corruption — satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimate `(raw_body, hmac)` pair, which any developer/merchant with the app installed on their own store can trivially capture (their own webhook deliveries are legitimate and fully attacker-controlled in timing/content for topics whose payload doesn't strictly have to embed the shop ID for it to be dangerous, e.g. generic content webhooks or product/webhook topics with attacker-influenced content). No secrets, tokens, or privileged access to another tenant are needed — only the ability to receive one's own valid webhook and replay it. This is a realistic capability for any unprivileged app-installing user.

### Recommendation
Bind the header-derived identity fields to the signed content instead of trusting raw headers post-HMAC-check:
- Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string used by `HmacValidator`, or
- Require the caller/host framework to independently verify that `request.shop` matches an expected/known shop for the delivery (e.g. compare against the shop the webhook was registered for), rather than trusting the header value alone once the body-only HMAC passes.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; app registers a webhook (e.g. `products/update`) whose body content the attacker can influence (e.g. by editing a product they control) and whose body does not embed shop-identifying claims validated elsewhere.
2. Shopify delivers the webhook to the app's endpoint with headers including:
   - `x-shopify-hmac-sha256: <valid HMAC of raw body using app's secret>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
3. Attacker captures this exact `raw_body` and `hmac` value.
4. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the same webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged shop header; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body against the HMAC — never the shop header: [4](#0-3) 
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, believing it to be an authentic webhook from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
