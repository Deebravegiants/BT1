### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface used by `HmacValidator.validate`, but its `to_signable_string` returns only the raw HTTP body, excluding the `shop`, `topic`, and `webhook_id` fields that are read from unauthenticated request headers and later acted upon by the handler. This breaks the identity binding: `hmac == HMAC(secret, body)` while the tenant identifier `request.shop` is never covered by that signature, so `shop_authenticated != shop_signed`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only the `@raw_body` is returned, whereas `shop`, `topic`, and `webhook_id` are parsed straight from attacker-reachable HTTP headers: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` and compares it against `request.hmac` — again, a function only of the body, not of `shop`: [3](#0-2) [4](#0-3) 

Once the HMAC check passes, `request.shop` (an unauthenticated header value) is forwarded verbatim to the app's webhook handler as the merchant/tenant identifier: [5](#0-4) 

Because a given app's `Context.api_secret_key` is shared across every shop that has installed the app (it is not a per-shop secret), any party that has legitimately installed the app on shop A can capture one valid `(body, hmac)` pair delivered to shop A's endpoint, then replay the identical body/HMAC to the same endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with victim shop B's domain. `HmacValidator.validate` will still succeed because the signature never bound `shop` in the first place, and `Registry.process` will invoke the handler with `shop: "shop-b.myshopify.com"`, causing the app to act on/associate data for a shop the attacker does not control.

### Impact Explanation
This is a cross-tenant identity-binding break: the value the library authenticates (the body, keyed by the app-wide shared secret) is not the same value the handler trusts as the tenant identity (the `shop` header). Any consumer of this gem that relies on `WebhookMetadata#shop` from `Registry.process` to select which merchant's records to update is exposed to cross-tenant webhook forgery/confusion, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Medium-to-High: exploitation only requires the attacker to be a legitimate installer of the same app on at least one shop (a normal, unprivileged position for any developer/merchant who can install the app), and to know the target's shop domain (typically public/knowable, e.g. `victim.myshopify.com`). No access token, `client_secret`, or privileged account is required — only reuse of a body/HMAC pair the attacker themselves legitimately received.

### Recommendation
Include the tenant-binding fields in the signed payload verified by `HmacValidator`, or otherwise cryptographically bind `shop` (and `topic`/`webhook_id`) to the HMAC check — e.g. change `Request#to_signable_string` to incorporate the shop domain (and topic) alongside the raw body, matching how `Oauth::AuthQuery#to_signable_string` includes `shop` in its signable string. At minimum, document and enforce that consumers must not trust `WebhookMetadata#shop` unless it is independently corroborated (e.g. cross-checked against a session store) rather than only HMAC-"validated" via a signature that never covers it.

### Proof of Concept
1. App has two installs: shop A (`shop-a.myshopify.com`, attacker-controlled) and shop B (`shop-b.myshopify.com`, victim), both using the same app `client_secret`.
2. Shopify delivers a legitimate webhook to the app for shop A with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)` per `HmacValidator.compute_signature`.
3. Attacker captures `(B, H)` from their own shop A delivery (fully within their control since they own shop A).
4. Attacker sends a forged POST to the app's webhook endpoint with the identical raw body `B`, identical `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: shop-b.myshopify.com`.
5. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches `H` — validation succeeds, per [6](#0-5) .
6. `handler.handle` is invoked with `shop: "shop-b.myshopify.com"`, the body originally intended for shop A, causing the app to associate/act on attacker-controlled webhook content under victim shop B's identity, per [5](#0-4) .

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
