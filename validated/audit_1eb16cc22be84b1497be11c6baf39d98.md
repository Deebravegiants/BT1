### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) purely from the unauthenticated `shopify-shop-domain` HTTP header, while the HMAC signature that the gem validates (`Utils::HmacValidator.validate`) covers only the raw request body. Because the signing secret (`api_secret_key`) is shared across every shop that has installed the app, a valid `(body, hmac)` pair is not shop-specific. This breaks the identity binding: `shop authenticated by HMAC == shop the code trusts for tenant routing`.

### Finding Description
`Registry.process` authenticates a webhook only by checking the HMAC of the raw body: [1](#0-0) 

The signable content used for that check is defined as just the raw body: [2](#0-1) 

`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, to_signable_string)` and compares it to the value from the `shopify-hmac-sha256` header: [3](#0-2) 

However, the `shop` value that gets forwarded to the app's webhook handler (and is normally used to select the tenant record to mutate) is read straight from the `shopify-shop-domain` header, which is **not** included in `to_signable_string`: [4](#0-3) [5](#0-4) 

Because `api_secret_key` is a single, app-wide secret (not a per-shop secret), any shop that has installed the app can receive a legitimately-signed webhook body+HMAC pair from Shopify for its own store, then replay that exact body and HMAC to the app's webhook endpoint while substituting a different value in the `shopify-shop-domain` header. The HMAC check still passes (it never looked at that header), and `Utils::HmacValidator.validate` returns `true`, so `Registry.process` treats the forged shop-domain as authentic and dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: ..., ...)` to the app's handler with the attacker-chosen `shop`.

The equality that should hold — "the shop whose HMAC key produced this signature == the shop attributed to this webhook" — does not hold, because the signature only proves "signed by the app's shared secret," not "originated from shop X."

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who is a normal (unprivileged) installed merchant of the app can cause the app to process webhook data under a victim shop's identity. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (e.g., to update per-shop cached data, trigger shop-scoped side effects, or key database writes), this can lead to cross-tenant data corruption/confusion — one of the explicitly listed Critical impacts ("cross-tenant access").

### Likelihood Explanation
Likelihood is moderate-to-high in any app that relies on this gem's webhook shop attribution without independently cross-checking `shop` against session/tenant records tied elsewhere (e.g. an active session store), since the gem provides no protection here itself. Any merchant who installs the app can capture a valid `(raw_body, hmac)` pair from their own legitimate Shopify-delivered webhook (e.g. via network capture or their own server logs) and replay it with a modified header — no secrets, tokens, or privileged access required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed payload, or otherwise cryptographically bind the `shopify-shop-domain` header to the signed body before trusting it (e.g., validate `shop` against a known/registered shop list, or require the HMAC to be computed over `shop + topic + body` rather than body alone). At minimum, document prominently that `Request#shop` is not authenticated by the HMAC and that host apps must independently verify tenant ownership before acting on it.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker triggers a real event (e.g., updates a product) causing Shopify to send a legitimately signed webhook to the app's endpoint with headers:
   - `shopify-hmac-sha256: <valid HMAC of raw_body>`
   - `shopify-shop-domain: attacker-shop.myshopify.com`
   - `shopify-topic: products/update`
   and some `raw_body` JSON.
2. Attacker captures this exact `raw_body` and `shopify-hmac-sha256` value (both are attacker's own legitimate traffic, no secret needed).
3. Attacker replays the same request to the app's public webhook endpoint, changing only `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`: [6](#0-5) 
   This passes because it only re-hashes `raw_body`, which is unchanged and still matches the supplied HMAC.
5. The app's handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON> ...)` — the gem asserts this webhook is authentically from `victim-shop`, even though it was forged by an unrelated, unprivileged merchant.

### Citations

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
