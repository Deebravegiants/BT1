Confirmed root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `topic`, `shop`, `webhook_id`, and `api_version` are read straight from HTTP headers via `shopify_header` (`lib/shopify_api/webhooks/request.rb:15-33`) and are never included in the HMAC-signed payload. `Registry.process` validates only the body HMAC (`lib/shopify_api/webhooks/registry.rb:190`) and then trusts `request.shop`/`request.topic` to build `WebhookMetadata` (`lib/shopify_api/webhooks/registry.rb:198-199`), which is exactly the "field acted on but not covered by the HMAC" identity-binding break called out in the rules.

### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw body alone, never from the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body HMAC is valid and then unconditionally trusts those headers to build the `WebhookMetadata` passed to the host app's handler.

### Finding Description
`to_signable_string` in `lib/shopify_api/webhooks/request.rb:35-38` returns only `@raw_body`:
```ruby
def to_signable_string
  @raw_body
end
```
`Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) recomputes the HMAC over exactly that string and compares it to the `x-shopify-hmac-sha256`/`shopify-hmac-sha256` header. Because only the body is signed, the identity fields `shop`, `topic`, `webhook_id`, and `api_version` — all read directly from unauthenticated headers via `shopify_header` (`lib/shopify_api/webhooks/request.rb:20-33`) — carry no cryptographic binding to the signature at all.

`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) validates the HMAC and then does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
The equality that should hold — `hmac-covered bytes == bytes used to determine which shop/topic the data belongs to` — is broken: `hmac-covered bytes = raw_body` but `identity fields used by handler = header values`, which are disjoint from the signed content.

Any party who can obtain one legitimately HMAC-valid webhook body for the app's `client_secret` (e.g., a merchant who has installed the app and genuinely receives webhooks for their own shop, or any actor able to capture/replay a delivered webhook payload) can resend that exact body with the `shop-domain` header rewritten to any other shop, or the `topic`/`webhook-id` headers rewritten to any other registered topic/id, and the request will still pass `HmacValidator.validate` because the signature only ever covered the body bytes.

### Impact Explanation
This crosses the tenant boundary the gem is meant to enforce for webhook processing: the app's own handler is told a payload belongs to shop A (or topic A) when it was actually signed as belonging to shop B (or topic B). Depending on how the host app uses `WebhookMetadata#shop`/`#topic` (e.g., looking up per-shop session/access tokens, writing to per-tenant data stores, deduplicating with `webhook_id`), this enables cross-tenant data confusion/injection — data destined for one merchant's records gets attributed to another merchant purely because the gem exposes unauthenticated header values as if they were verified identity fields. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Medium-to-high: exploitation requires possession of at least one validly-signed webhook body (trivial for any legitimate merchant/installer of the app, since Shopify sends real webhooks to real installs), plus the ability to alter HTTP headers on the replayed request — both are within reach of an unprivileged actor who has installed the target app, with no access token, `client_secret`, or TLS interception needed.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed payload used by `to_signable_string`, or otherwise cryptographically bind them to the verified body (e.g., verify that `shop`/`topic` match values embedded in the signed body/metadata Shopify provides) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real event so Shopify delivers a genuine webhook with a valid `x-shopify-hmac-sha256` for body `B`.
2. Attacker captures the raw request (body `B`, valid HMAC header, `x-shopify-shop-domain: attacker-shop.myshopify.com`).
3. Attacker resends the identical body `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`/`x-shopify-webhook-id`).
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:27-31`) recomputes HMAC over `@raw_body` only, which still matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) accepts the request.
5. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` even though the signed body never originated as a webhook for `victim-shop.myshopify.com`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
