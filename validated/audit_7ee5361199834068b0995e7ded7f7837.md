### Title
Webhook shop/topic/webhook-id headers are trusted for tenant identification without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used for tenant/topic identification are taken directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then unconditionally trusts these header-derived values when dispatching to the host app's webhook handler, so the identity binding "verified bytes == acted-upon shop identity" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `#hmac`, `#topic`, `#shop`, `#api_version`, `#webhook_id` are all read from HTTP headers that are not part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` calls `Utils::HmacValidator.validate(request)`, and once it passes, forwards `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the verified bytes — straight into the handler: [4](#0-3) 

This breaks the intended binding: `shop authenticated (bytes covered by HMAC) == shop acted on (header value dispatched to the handler)`. Concretely, `shop-domain == body` is never checked; only `hmac(body, secret) == hmac_header` is checked. An attacker who can obtain any single legitimate `(raw_body, hmac)` pair signed with the app's `api_secret_key` (e.g., a webhook delivered to their own development store/test app using the same Shopify app credentials, or a captured request during normal, non-privileged use of the app) can replay that exact body/HMAC pair while swapping the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to any value. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` will dispatch the handler with the attacker-chosen `shop` value.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to select which merchant/tenant record to update (the documented and expected usage pattern for this gem, per `docs/usage/webhooks.md` and the `shop:` field passed in `Registry.process`), an attacker who legitimately owns one shop/session for the app can trick the webhook processing pipeline into associating that payload with an arbitrary other shop domain string, since the shop identity is never part of the authenticated payload. This yields cross-tenant confusion: data or actions intended for shop A get applied under an attacker-chosen shop B identifier, without needing the app's `client_secret` or any additional secret material — only a single legitimately-signed payload from any shop using the same app.

### Likelihood Explanation
Moderate: exploitation requires the attacker to be able to send crafted HTTP requests directly to the webhook endpoint (bypassing the front-end but not the underlying secret) and to have obtained at least one legitimately HMAC-signed `(body, hmac)` pair for the app (e.g., from their own store/session, which any developer/merchant of the app can generate). No brute-forcing of the secret is required since the header fields are simply unauthenticated metadata that the library does not bind to the signed body.

### Recommendation
Include the identity-critical headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed content, or otherwise cryptographically bind them to the payload before use, rather than trusting them as separate, unauthenticated header values in `ShopifyAPI::Webhooks::Request`. At minimum, document that host applications must independently verify `shop-domain` against a known/authorized shop for their app before acting on webhook data, and highlight that `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` does not protect header values.

### Proof of Concept
1. An attacker who operates their own shop A obtains a valid webhook delivery to their configured endpoint: `raw_body = "{...}"`, header `x-shopify-hmac-sha256 = HMAC(raw_body, api_secret_key)` and `x-shopify-shop-domain = "shopA.myshopify.com"`.
2. The attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` value to the victim app's webhook endpoint, but sets `x-shopify-shop-domain: shopB.myshopify.com` (a shop domain the attacker does not own/control) and/or a different `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses the headers with no cross-check between `shop-domain` and the body.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only — it matches, since `raw_body` and `hmac` are unmodified — and processing proceeds: [5](#0-4) 
5. The registered handler receives `WebhookMetadata` with `shop: "shopB.myshopify.com"` even though the payload was never signed for/verified against shop B, allowing the attacker to inject data under an arbitrary shop identity into the host app's webhook processing logic.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
