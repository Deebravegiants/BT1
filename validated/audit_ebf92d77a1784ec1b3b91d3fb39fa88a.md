### Title
Webhook shop domain/topic headers are trusted but excluded from the HMAC binding - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from unauthenticated HTTP headers, while `to_signable_string` used by the HMAC check binds only the raw body. `Registry.process` validates the HMAC and then dispatches the handler using these header-derived values as if they were verified, breaking the equality "bytes verified == bytes acted on."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are included in the signable string: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` — which recomputes the HMAC over `to_signable_string` (i.e., the raw body only) — and then immediately trusts `request.topic` and `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and compares it to the `hmac` header: [4](#0-3) 

This is precisely the "field acted on but not covered by the HMAC" class from the rules: the byte range that is cryptographically verified (the JSON body) is disjoint from the byte range that is acted on (the `shop`/`topic` headers used for tenant/topic dispatch). Any entity capable of delivering a single byte-for-byte-valid `(raw_body, hmac)` pair to the app's webhook endpoint — including a party that merely captures or replays one genuinely-signed webhook delivery for their own shop — can attach arbitrary `x-shopify-shop-domain` / `x-shopify-topic` headers, and the gem will treat the resulting `WebhookMetadata` as authenticated for a different shop/topic than the one Shopify actually intended.

### Impact Explanation
This crosses the tenant boundary that the gem is expected to enforce: apps rely on `WebhookMetadata#shop` from `Registry.process` to route/attribute the payload to the correct merchant. Because the shop header is outside the signed byte range, the gem itself provides no assurance that the `shop` field it hands to the handler corresponds to the shop that actually generated (and whose secret validated) the body. This falls under "cross-tenant access" impact — data or actions intended for tenant A can be attributed to/processed under tenant B's identity purely by header substitution, without needing the app's `client_secret` or any credential beyond a single valid webhook delivery.

### Likelihood Explanation
Exploitation requires an attacker to be able to submit a request to the app's webhook endpoint with a valid `(raw_body, hmac)` pair paired with attacker-chosen headers. This is realistic in any deployment where the webhook endpoint is reachable and where a previously-observed/legitimately-delivered webhook body+hmac (e.g. from the attacker's own shop test event) can be resent with modified headers, since nothing in the gem re-derives or checks the headers against the signed payload. No secret material is required, only a captured valid delivery.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable payload used for HMAC verification, or otherwise cryptographically bind them to the body before `Registry.process` trusts them, e.g., by having `to_signable_string` concatenate the raw body with the header values used for dispatch, and rejecting requests where the recomputed signature does not match. At minimum, document and/or enforce that consumers must independently re-validate `shop`/`topic` against out-of-band trusted metadata before acting on `WebhookMetadata`.

### Proof of Concept
1. Attacker's own shop installs the app and triggers a webhook event (e.g. `orders/create`), producing a legitimately-signed delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`.
2. Attacker captures this `(B, hmac)` pair (e.g., via any endpoint/logging surface that echoes it, or a replay/resend feature).
3. Attacker sends a new POST to the app's webhook endpoint with the same `B` and `hmac`, but with `x-shopify-shop-domain` set to a victim shop's domain and/or `x-shopify-topic` changed.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `hmac` (lib/shopify_api/utils/hmac_validator.rb:12-31).
5. `Registry.process` builds `WebhookMetadata.new(topic: <attacker-chosen>, shop: <victim shop>, body: parsed(B), ...)` (lib/shopify_api/webhooks/registry.rb:188-200) and invokes the handler as if it were an authentic webhook for the victim shop/topic.

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
