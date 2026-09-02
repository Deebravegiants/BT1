### Title
Webhook `shop` (tenant identity) is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the `shop` (tenant) identifier used to route and act on the webhook is read from an HTTP header that is never covered by that signature. Any actor who can obtain one validly-signed webhook (e.g. by installing the app on their own store) can replay the same signed body while forging the `shop-domain` header to impersonate a different merchant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from headers that are not part of the signed material: [2](#0-1) 

`Registry.process` validates only this body-only HMAC and then dispatches the handler using `request.shop` as the tenant identity, with no cross-check that the header-derived shop is bound to the signature: [3](#0-2) 

`HmacValidator.validate` simply recomputes HMAC over `to_signable_string` (the raw body) and compares it to the `hmac` header value — it has no notion of `shop`: [4](#0-3) 

The identity binding that should hold is:
`HMAC-verified bytes == bytes that determine the tenant ("shop") the app acts on`

In practice the binding is broken:
`HMAC(raw_body, secret) == valid` while `shop = header["shop-domain"]` (unauthenticated, attacker-controlled on replay).

An unprivileged attacker who installs the target app on their own development/test store receives genuine webhook deliveries with a valid `X-Shopify-Hmac-Sha256` signature for that body. Because the signature never incorporates the `X-Shopify-Shop-Domain` header, the attacker can replay the exact same (body, hmac) pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` value for a victim shop. `Utils::HmacValidator.validate(request)` still returns `true` (the body bytes and signature are unchanged), and `Registry.process` forwards `WebhookMetadata.new(..., shop: request.shop, ...)` — the forged shop — to the app's handler.

### Impact Explanation
This crosses a tenant boundary without any credential belonging to the victim: the app's webhook handler will process attacker-supplied data as if it originated from a different merchant. Depending on how the hosting app uses `WebhookMetadata#shop` (e.g., to look up/mutate per-shop records, or to process compliance topics like `shop/redact`/`customers/redact`/`app/uninstalled`), this can lead to cross-tenant data corruption or triggering of destructive/compliance actions against a shop the attacker does not own. This matches the High-severity class "credential/tenant boundary crossed without the corresponding proof" analogous to the referenced report's core theme of a check being performed against the wrong/uncovered field.

### Likelihood Explanation
Likelihood is high for any attacker able to install the app on a store they control (the normal, unprivileged path to becoming an app user) — no `api_secret_key`, access token, or social engineering is required. Replaying an HTTP POST with a modified header while keeping the body and its legitimate signature intact is trivial.

### Recommendation
Bind the `shop` (and `topic`) to the signed material, or otherwise authenticate the header value against the signature, e.g.:
- Include `shop-domain` (and `topic`) in the HMAC-signed string, or
- Verify the shop header against session/shop records established via a properly authenticated channel (OAuth/token exchange) before trusting it, rather than trusting it purely because the body HMAC matches.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`. Shopify sends a real webhook, e.g. `orders/create`, to the app's endpoint with:
   - Header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - Header `X-Shopify-Hmac-Sha256: <valid hmac of raw body>`
   - Body: `{"id": 1, ...}` (attacker fully controls order content in their own store)
2. Attacker replays the identical request to the same endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, keeping body and `X-Shopify-Hmac-Sha256` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4)  — this passes because it only checks `raw_body` against the unchanged HMAC.
4. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, even though `victim-shop` never sent this webhook. [6](#0-5)

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
