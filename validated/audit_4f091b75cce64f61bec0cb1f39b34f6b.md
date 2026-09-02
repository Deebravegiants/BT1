Confirmed: the webhook HMAC signature (`Utils::HmacValidator.validate`) is computed only over `to_signable_string`, which for `ShopifyAPI::Webhooks::Request` is the raw request body [1](#0-0) . The `shop` value handed to the webhook handler comes from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is not part of the HMAC-signed material at all [2](#0-1) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e. body integrity/authenticity) before dispatching `request.shop` straight to the merchant's handler [3](#0-2) .

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw body [4](#0-3) . The `shop` field that is delivered to the app's `WebhookHandler` (used by hosts to select per-tenant data/session) is read straight from the `x-shopify-shop-domain` header and is never included in the signed bytes [5](#0-4) . This breaks the identity binding: `HMAC-verified bytes == raw_body` but `shop == unauthenticated header`, so `shop` is a field acted on but not covered by the HMAC.

### Finding Description
`VerifiableQuery#to_signable_string` for `Webhooks::Request` returns only `@raw_body` [1](#0-0) . `HmacValidator.validate` computes `HMAC(api_secret_key, to_signable_string)` and compares it to the `hmac` header using `OpenSSL.secure_compare` [6](#0-5) . Because `shop`, `topic`, `webhook_id`, and `api_version` are pulled from separate, unsigned headers (`shopify_header`) [7](#0-6) , any request whose body+HMAC pair is valid for the app's `client_secret` will pass validation regardless of what `shop` header accompanies it. `Registry.process` then constructs `WebhookMetadata` with that unauthenticated `shop` value and invokes the app's handler [8](#0-7) .

An attacker who is a legitimate (even unprivileged) merchant can install the target app on their own store, capture one authentic `(raw_body, hmac)` pair from a webhook Shopify sent them, and then submit that exact body+hmac to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with the victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body against the secret, not the shop. The library then hands the handler a `WebhookMetadata` claiming the victim's shop but carrying the attacker's payload, i.e. it lets attacker-controlled webhook content masquerade as belonging to another tenant.

### Impact Explanation
This is a cross-tenant identity confusion at the library layer: the field host applications rely on (`shop`) to key per-tenant session/data lookups is not part of the authenticated payload. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up the session/token for that shop, or to attribute the webhook body to that shop's records), this can lead to cross-tenant data corruption or processing legitimate-looking-but-forged events under another merchant's identity.

### Likelihood Explanation
Medium: it requires the attacker to be able to install the app themselves (any merchant can do this — no privileged credentials needed) and to be able to send an arbitrary HTTP POST with attacker-chosen headers to the app's public webhook receiver endpoint, which is by design internet-reachable.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind them to the body — e.g., verify the HMAC over `shop + raw_body`, or require the host app to independently confirm the header-derived `shop` against a value derived from signed data before trusting it. At minimum, document that `WebhookMetadata#shop` is not itself authenticated and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. App merchant M installs the target app; Shopify sends a real webhook with `raw_body = B` and `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain = m.myshopify.com`.
2. Attacker (= M, or anyone who intercepted this legitimate webhook) POSTs to the app's webhook endpoint with the same `B` and same HMAC header, but sets `x-shopify-shop-domain = victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` [1](#0-0)  — validation passes.
4. `request.shop` returns `"victim.myshopify.com"` from the unsigned header [2](#0-1) , and `handler.handle` is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: <attacker's parsed body> ...)` [9](#0-8) , even though the payload actually originated for the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
