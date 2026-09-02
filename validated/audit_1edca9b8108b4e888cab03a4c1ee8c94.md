### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are taken directly from HTTP headers, are never included in the signed content and are handed to the app's webhook handler as if they were verified.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable content as the raw body only: [1](#0-0) 

All the identity-carrying fields are read straight off unauthenticated headers, with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which only checks `hmac == HMAC(secret, to_signable_string)` i.e. `HMAC(secret, raw_body)`: [3](#0-2) [4](#0-3) 

Once the body's HMAC passes, `request.shop`, `request.topic`, and `request.webhook_id` (all header-derived, unsigned) are forwarded verbatim to the handler as `WebhookMetadata`: [5](#0-4) 

The broken identity binding, stated as an equality:
- Intended: `verified(body, shop, topic, webhook_id) == HMAC(secret, body || shop || topic || webhook_id)`
- Actual: `verified(body) == HMAC(secret, body)`, while `shop`, `topic`, `webhook_id` are accepted unauthenticated.

Because `shop` is not part of the signed material, any (body, hmac) pair that is valid for one shop's webhook remains a *valid HMAC* even when replayed with a different `x-shopify-shop-domain` header. The gem has no mechanism to detect that the header was swapped.

### Impact Explanation
An unprivileged actor who can obtain any single legitimately-signed (body, hmac) pair for the target app (e.g., by installing the app on their own store — a normal, unprivileged action — and capturing a real webhook delivery to their own endpoint) can replay that exact body+hmac to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header to impersonate an arbitrary victim shop. `Registry.process` will accept the HMAC (it only checks the body) and dispatch the payload to the registered handler tagged with the attacker-chosen `shop`. Any host application that uses `WebhookMetadata#shop` to scope side effects (loading/mutating that shop's session, updating shop-specific data, honoring `app/uninstalled` to wipe credentials, etc., as the field is explicitly designed for) can be made to act on behalf of, or against, a shop the attacker does not control. This is a cross-tenant identity spoofing vector reachable by an ordinary internet/app user without any credentials, access tokens, or `client_secret`.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: obtaining one valid signed webhook body is trivial for anyone who can install the app on a free/dev shop (a normal, unprivileged flow), and replaying an HTTP POST with modified headers requires no special access. The main constraint is that the *body content* of the replayed event stays as originally signed (only headers can be forged), which limits which topics are most useful to spoof, but topics like `app/uninstalled` or ones whose handler logic keys almost entirely off `shop` (ignoring body specifics) are directly exploitable.

### Recommendation
Bind the shop/topic identity to the signed content instead of trusting headers unconditionally:
- Require the app to independently confirm that `shop` in `WebhookMetadata` corresponds to a shop with an active, previously stored session/installation before honoring destructive or state-changing actions triggered by webhook headers.
- At minimum, document/enforce that `request.shop`/`topic`/`webhook_id` are NOT covered by the HMAC and must not be treated as authenticated, or extend the signable string (where compatible with Shopify's signing scheme) to include these headers so tampering is detectable.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` (no privilege required) and lets Shopify deliver a normal webhook (e.g. `orders/create`) to the app's webhook endpoint. Attacker captures the raw request: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's secret), along with `X-Shopify-Topic` and `X-Shopify-Webhook-Id`.
2. Attacker crafts a new POST to the same webhook endpoint using the identical body `B` and `H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - (optionally) alters `X-Shopify-Topic` / `X-Shopify-Webhook-Id` to another registered topic/id, since none of these are covered by `H`.
3. `ShopifyAPI::Webhooks::Registry.process` computes `HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` (`B`) only — it matches `H`, so the request is accepted.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload was never issued by Shopify for that shop, allowing the attacker to trigger shop-scoped logic under a victim's identity.

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
