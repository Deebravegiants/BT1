Based on my investigation, I've confirmed the root cause and impact chain. This is a valid analog finding.

### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop` (tenant) identity is read from an unauthenticated HTTP header. Any host application that dispatches to per-shop business logic based on `WebhookMetadata#shop` (the documented, intended usage of this gem's webhook API) will trust a shop identifier that was never bound into the signature it validated.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Utils::HmacValidator.validate` computes the HMAC exclusively over this signable string using the app's `api_secret_key`, comparing it against `request.hmac` (itself parsed straight from the `x-shopify-hmac-sha256` header): [2](#0-1) .

The `shop` accessor, however, is derived purely from the `x-shopify-shop-domain` / `shopify-shop-domain` header, with no cryptographic binding to the HMAC at all: [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, without any secondary check tying the shop to the signed bytes: [4](#0-3) . `WebhookMetadata#shop` is a plain `const :shop, String` field with no additional integrity guarantee: [5](#0-4) .

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the gem verifies `hmac == HMAC(body, secret)` but then acts on `shop`, which is an entirely separate, unauthenticated input. Formally the gem should guarantee `shop == the tenant that the secret-holder (Shopify) actually signed for`, but it only guarantees `hmac == HMAC(body, secret)`; `shop` is disjoint from that equality.

Because the `api_secret_key` is shared across every shop that has installed the app, any merchant that installs the app can legitimately receive a Shopify-signed webhook for their own shop, capture the `(raw_body, hmac)` pair, and replay that exact same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` will report the signature as valid (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This breaks the shop-identity binding the whole webhook system exists to provide, and lets an attacker who controls one installed shop (an unprivileged tenant of the same app) inject a Shopify-signed-looking webhook that is misattributed to a different, victim shop. Any host application logic in `WebhookHandler#handle` that keys off `data.shop` for tenant-scoped operations — e.g. looking up a stored session/access token for that shop, updating shop-specific records, or triggering a shop-specific side effect — is done against attacker-chosen tenant identity, which is cross-tenant access (Critical-tier impact per the rules).

### Likelihood Explanation
The attacker only needs their own valid app installation (any merchant can install a public app) plus the ability to send arbitrary HTTP requests to the app's public webhook endpoint — no access token, no `api_secret_key`, and no privileged account is required. Capturing one legitimate `(body, hmac)` pair from their own shop's webhook deliveries is trivial (it's delivered straight to their own endpoint) and the payload can be replayed unmodified except for the header, since the HMAC never covers headers.

### Recommendation
Bind the `shop` value into the verified signature, or otherwise cryptographically tie the shop-domain to the request before trusting it — e.g. maintain (and require) a per-shop webhook secret, or reject/flag processing when the `shop` header does not match a value independently verifiable from the signed body (Shopify's raw webhook body typically embeds `"myshopify_domain"`/`"admin_graphql_api_id"` fields for orders, but for topics lacking a shop identifier in the payload, add explicit documentation instructing consumers that `data.shop` is unauthenticated and must not be used alone to select tenant-scoped credentials, or extend `HmacValidator`/`Request` to also authenticate the shop-domain header as part of the signable string when Shopify supports doing so).

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`. Attacker registers a webhook (e.g. `orders/create`) pointing to the app's endpoint.
2. Shopify sends a webhook to the app for `attacker-shop.myshopify.com` with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, and some JSON `raw_body`.
3. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value from this legitimate delivery.
4. Attacker replays an HTTP POST to the same endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only checks `HMAC(raw_body, api_secret_key) == received_hmac` — this passes because `raw_body` and `hmac` are unchanged. `Registry.process` then builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` [6](#0-5)  and invokes the app's handler, which processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

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
