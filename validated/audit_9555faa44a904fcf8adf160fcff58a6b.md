### Title
Webhook `shop` (and `topic`/`webhook_id`) header trusted for tenant routing despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, then hands `request.shop`, `request.topic`, and `request.webhook_id` straight to the app's handler as trusted tenant-identifying metadata. However, the HMAC signature only ever covers the raw request body — not these headers — so the "authenticated" webhook and the "shop it's attributed to" are two different, unequal things.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `hmac` is read straight from the `hmac-sha256` header [2](#0-1) . `HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the body) and compares it to the `hmac` header [3](#0-2) . The `shop`, `topic`, and `webhook_id` values are read from separate, unsigned headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) [4](#0-3) .

`Registry.process` only checks the body HMAC, then dispatches to the handler using the unsigned `request.shop` and `request.topic` as the tenant/topic identity: [5](#0-4) . Nothing binds `shop`/`topic`/`webhook_id` to the signed body — the identity equality the gem implicitly assumes is:

`hmac_valid(body) == shop_header_is_trustworthy`

but that equality does not hold: `hmac_valid(body)` only proves *someone holding `api_secret_key` produced this exact body bytes at some point*; it says nothing about which shop or topic that body was originally sent for.

### Impact Explanation
An unprivileged internet user who is a legitimate (but low-privilege) installer of the target app on **their own** Shopify store receives genuine webhook deliveries — valid `(raw_body, hmac)` pairs signed with the app's `api_secret_key` — for their own shop's events. Because the signature covers only the body, that same `(raw_body, hmac)` pair remains valid regardless of which headers accompany it. The attacker can replay it to the app's webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop (and/or a forged `x-shopify-topic`/`x-shopify-webhook-id`). `Registry.process` will pass HMAC validation and invoke the handler with `WebhookMetadata` claiming the victim shop as the source [6](#0-5) , causing cross-tenant data injection/attribution inside the host application (e.g., writing data, triggering redaction/GDPR flows, or firing shop-scoped business logic under a victim's identity) — a cross-tenant integrity/authentication issue.

### Likelihood Explanation
Moderate-to-high: obtaining a valid `(body, hmac)` pair requires no secret knowledge — merely installing the app on one's own store (the normal, unprivileged path for any public app) and capturing one legitimate webhook delivery. Replaying it with a spoofed shop header is a trivial HTTP request; nothing in `Request` or `Registry` cross-checks header/body consistency.

### Recommendation
Bind the shop/topic/webhook_id to the cryptographic proof, not just the body: include these fields (or at minimum the shop domain) in the signable string used for HMAC computation, or require the calling application to independently verify that `request.shop` corresponds to a shop with an active, stored session/webhook registration for the given `webhook_id`/topic before trusting it. Document explicitly (and enforce in `Registry.process`) that `shop` is unauthenticated header data and must be cross-validated against the app's own session store.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal, unprivileged public-app install).
2. Shopify sends a real webhook to the app's endpoint:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {"id":123,"note":"hello"}
   ```
   Attacker captures this raw body + `hmac-sha256` header.
3. Attacker resends the exact same body and `hmac-sha256` value to the same endpoint but with:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the body against the same secret — it never inspects `shop-domain`. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the registered handler with `shop: "victim-shop.myshopify.com"`, and the host app processes/persists data as if it originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
