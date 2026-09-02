I found a solid analog: the webhook signature validation binds only the request body, but the `shop` identity used for tenant attribution is taken from an unsigned header.### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the unsigned `X-Shopify-Shop-Domain` header as the tenant identity handed to the app's handler. Because the HMAC secret (`Context.api_secret_key`) is the same for every shop that installs the app, an attacker who controls one (their own) shop can capture a legitimate, validly-signed webhook and replay its body with a forged `shop-domain` header pointing at a different, victim shop. The gem will report the HMAC as valid and dispatch the payload as if it originated from the victim tenant.

### Finding Description
The interest-rate report's bug class is "the field that matters is not the field that's authenticated." Here the analogous identity binding is:

`hmac(raw_body, api_secret_key) == valid` ⇏ `shop-domain header == authentic tenant`

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are never included in the signed string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, i.e. against `to_signable_string` (the body only), and then immediately forwards `request.shop` — the unauthenticated header — into `WebhookMetadata`, which is the object handed to the app's handler as the trusted tenant identity: [3](#0-2) 

`WebhookMetadata.shop` is declared as a trusted `const` field consumed by any `WebhookHandler#handle` implementation: [4](#0-3) 

`HmacValidator.validate` only proves the body was signed by *some* shop using this app (since the secret is shared across all merchants of the app) — it proves nothing about which shop the header claims: [5](#0-4) 

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` (and `host`) *are* included in the signed string used for the OAuth-callback HMAC check, correctly binding the identity to the signature: [6](#0-5) 

The webhook path has no equivalent binding: `shop` is asserted-but-not-authenticated, exactly the "field acted on but not covered by the HMAC" pattern called out in scope.

### Impact Explanation
Impact is Critical: **cross-tenant access**. An attacker who legitimately installs the target app on their own (attacker-controlled) shop will receive real, validly-HMAC-signed webhooks from Shopify for that shop. Because the app's `api_secret_key` used to compute the HMAC is identical for every merchant of the app, the attacker can take that valid `(raw_body, hmac)` pair and re-POST it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header with an arbitrary victim shop domain. `HmacValidator.validate` still returns `true` (it only checks the body), so `Registry.process` dispatches the payload to the handler tagged with the victim's `shop` value. Any app logic that uses `WebhookMetadata#shop` to select the tenant record, apply state changes, or fan out data (e.g., "mark order X as paid for shop Y", "update inventory for shop Y") will act on the wrong tenant using attacker-supplied body content — a direct violation of the tenant boundary enforced by the gem's own webhook verification API.

### Likelihood Explanation
High. Any developer/merchant can install the target app on a store they control and thereby obtain arbitrarily many legitimately-signed webhook bodies for arbitrary topics. Forging the HTTP headers on a replayed request requires no cryptographic material beyond what Shopify already delivered to the attacker. The vulnerable code path (`Request#to_signable_string` / `Registry.process`) is exercised on every webhook delivery, so no unusual or hard-to-reach condition is needed.

### Recommendation
Bind the tenant-identifying headers into the HMAC-signed string (or otherwise verify `shop-domain` against out-of-band trusted state), e.g.:

```diff
 def to_signable_string
-  @raw_body
+  "#{shop}\n#{topic}\n#{@raw_body}"
 end
```

and require the app-side webhook secret/HMAC computation to be regenerated to cover these fields, matching the pattern already used for `Auth::Oauth::AuthQuery`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and that consuming apps must independently confirm the shop is one they have an active session/installation for before trusting webhook content tied to that shop.

### Proof of Concept
1. App developer installs the target Shopify app on `attacker-shop.myshopify.com` (an unprivileged action any developer can perform) and registers a webhook, e.g. `orders/create`.
2. Shopify delivers a real webhook to the app's endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-of-raw-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: abcd-1234
   Body: { "id": 1, "total_price": "9999.00", ... }
   ```
   Attacker captures the raw body and the valid `X-Shopify-Hmac-Sha256` value (they control this shop, so they can view/log the raw request, e.g. via a request-logging proxy in front of their own app instance in a test environment, or by having their own handler log/echo it).
3. Attacker replays the identical body and HMAC to the same app endpoint, changing only the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac-of-raw-body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: abcd-1234
   Body: { "id": 1, "total_price": "9999.00", ... }
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over `request.to_signable_string` (the raw body only) and returns `true`, since the body/HMAC pair is unchanged: `lib/shopify_api/utils/hmac_validator.rb` lines 12-31; `lib/shopify_api/webhooks/request.rb` lines 35-38.
5. `Registry.process` proceeds and calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`: `lib/shopify_api/webhooks/registry.rb` lines 188-199 — the app now processes attacker-controlled order data as belonging to `victim-shop.myshopify.com`, crossing the tenant boundary the HMAC check was supposed to enforce.

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
