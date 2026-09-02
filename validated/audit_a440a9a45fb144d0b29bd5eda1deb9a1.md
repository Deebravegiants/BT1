Found a confirmed analog: the webhook `topic` and `shop-domain` headers used by `Registry.process` are not covered by the HMAC signature, matching the report's core defect (an authorization-relevant field that is checked/acted on but not covered by the integrity check).

### Title
Webhook `topic` and `shop-domain` headers are trusted for handler dispatch without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request by checking only the HMAC over the raw request body, then dispatches based on the `topic` and `shop` values taken from unauthenticated HTTP headers, mirroring the report's root cause: state (`YieldToken.yieldManager`/`relayer`) that can only legitimately be set by an authorized party but the binding that should enforce this is missing/broken.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#topic`, `#shop`, `#webhook_id`, `#api_version` are all read straight from HTTP headers (`shopify_header`) that are never mixed into the signed string [2](#0-1) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which calls `request.to_signable_string` (body only) and `request.hmac` — and then immediately uses `request.topic` to select the handler and passes `request.shop`, unverified, straight into the handler payload as `WebhookMetadata` [3](#0-2) . `Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, signable_string)` purely over that signable string and compares it with `OpenSSL.secure_compare` [4](#0-3) . Because the signature check binds only the body, any attacker who can produce a body/HMAC pair valid for one topic (or replay a genuine webhook's body+HMAC) can pair it with arbitrary `x-shopify-topic` and `x-shopify-shop-domain` header values, and the gem will treat the request as authentic for that attacker-chosen topic/shop.

Equality that should hold but doesn't: `hmac == HMAC(secret, topic ‖ shop ‖ body)` is required for the dispatch decision, but the gem only checks `hmac == HMAC(secret, body)`; `topic` and `shop` are unauthenticated inputs used post-verification exactly like the `YieldToken` owner-gated setters that had no binding back to `YieldManager`.

### Impact Explanation
This is a cross-tenant/authentication-boundary issue: handler code that expects `data.shop` to be the shop the HMAC-verified body came from can be tricked into acting "as" a different shop, and the topic-based dispatch can route a validly-signed body from one legitimate webhook to a completely different handler intended for another topic. Depending on host-app handler logic (e.g., `customers/redact`, `shop/redact`, order/inventory handlers keyed by `data.shop`), this can lead to cross-tenant data corruption or processing under a false shop identity — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged internet user who can reach the app's webhook endpoint can send arbitrary headers alongside a body; they only need one previously-observed valid `(body, hmac)` pair (webhooks are frequently non-secret in transit, or an attacker with even one legitimate low-privilege webhook subscription can harvest a valid signed body) to remix headers freely, since the gem never re-derives or checks that `topic`/`shop` are consistent with the signed payload's own claims. This requires no `api_secret_key`, access token, or privileged account — only the ability to send HTTP requests to the host app's webhook route, which is the intended entry point for Shopify-originated webhooks.

### Recommendation
Include the `topic` and `shop-domain` header values (and ideally `webhook-id`) in the HMAC-signed string, or otherwise cryptographically bind them to the body before trusting them for dispatch, analogous to fixing the missing ownership-transfer binding in the report by ensuring the value acted upon is provably tied to the authenticated source.

### Proof of Concept
1. Observe/capture one legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S`), originally sent with `x-shopify-topic: orders/create` and `x-shopify-shop-domain: victim-shop.myshopify.com`.
2. Replay a POST to the app's webhook endpoint with the *same* body `B` and *same* `H`, but attacker-controlled headers `x-shopify-topic: shop/redact` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` computes `HMAC(S, B)` and compares to `H` — it matches because the body is unchanged [4](#0-3) .
4. `Registry.process` proceeds, looks up the handler for `shop/redact` (attacker-chosen topic) and invokes it with `shop: "attacker-shop.myshopify.com"` in the `WebhookMetadata`, even though the signed body `B` never certified either value [3](#0-2) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
