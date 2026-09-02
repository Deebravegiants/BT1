### Title
Webhook shop identity spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `HmacValidator` binds solely to the body bytes. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are read separately and passed unverified into the handler. Because a single app has one `client_secret` shared across every shop that installs it, any tenant of the app can compute (or simply capture) a valid body+HMAC pair from their own legitimate webhook traffic and replay it against the app's public webhook endpoint with a different `shop-domain` header, causing the app to attribute another merchant's webhook data/action to the attacker-chosen shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` establish what is "covered" by the signature check: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively from `to_signable_string` (the body) and compares it with the `hmac` header: [2](#0-1) 

`Registry.process` accepts the request once that body-only HMAC check passes, then builds `WebhookMetadata` from `request.shop`, `request.topic`, and `request.webhook_id` — none of which participated in the signature: [3](#0-2) 

The identity binding that should hold is: `HMAC-verified authenticity == (shop, topic, body)` as a single unit. Instead the gem verifies `HMAC-verified authenticity == body` and trusts `shop` as an independent, unauthenticated header value. Since the app's `client_secret` (and therefore the HMAC key) is identical for every shop that installs the app, any shop that legitimately receives a signed webhook (with valid body+HMAC) can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The signature will still validate — it never depended on the shop value — and the handler will process the payload as if it originated from the spoofed shop.

### Impact Explanation
This breaks the tenant boundary the webhook processing pipeline is supposed to enforce: data or actions meant for shop A can be attributed to shop B purely by an unprivileged (but existing) app installer forging the shop header on a replayed, still-validly-signed body. Depending on how the host app persists or acts on webhook data keyed by `shop`, this enables cross-tenant data corruption or cross-tenant action execution — a Critical-tier cross-tenant access impact.

### Likelihood Explanation
Any merchant/tenant that has legitimately installed the app receives real webhook traffic (valid body+HMAC) they can capture and replay. No access to `api_secret_key`, tokens, or privileged accounts is required beyond being an ordinary installer of the multi-tenant app, and the webhook endpoint is by design internet-reachable.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`) in the signed string that is HMAC-validated, or otherwise cryptographically bind the shop identity to the verified payload before dispatching to handlers, so a valid signature cannot be replayed across shop boundaries.

### Proof of Concept
1. App X is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (same `client_secret` for both, per Shopify's per-app secret model).
2. The owner/operator of `shop-a` receives a legitimate webhook: `POST /webhooks` with body `B`, header `shopify-hmac-sha256: H` (valid), `shopify-shop-domain: shop-a.myshopify.com`.
3. That operator resends the identical `body: B` and `shopify-hmac-sha256: H` to the app's webhook endpoint but sets `shopify-shop-domain: shop-b.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` re-computes the signature from `B` only and it matches `H`, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the handler with `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` while the body content actually belongs to `shop-a`.

### Citations

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
