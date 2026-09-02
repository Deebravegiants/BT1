This gem's webhook signature verification suffers from the same "field acted on but not covered by the authentication check" flaw as the reported COMP bug — here the fields used to attribute a webhook to a shop/topic aren't part of what's cryptographically bound by the HMAC. [1](#0-0) 

## Title
Webhook shop/topic identity is not HMAC-bound, enabling cross-tenant webhook payload replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC solely over that raw body. `Request#shop`, `Request#topic`, and `Request#webhook_id`, however, are read directly from unauthenticated HTTP headers and are never included in the signed bytes. [2](#0-1) [3](#0-2) 

### Finding Description
`Registry.process` validates the request purely by checking `Utils::HmacValidator.validate(request)`, which recomputes an HMAC over `request.to_signable_string` (the raw body only) and compares it against `request.hmac` (derived from the `x-shopify-hmac-sha256` header): [4](#0-3) 

After this check passes, `Registry.process` dispatches to the handler using `request.shop` and `request.topic`, which are taken straight from the `x-shopify-shop-domain` and `x-shopify-topic` headers — neither of which is part of the signed payload: [5](#0-4) 

The equality the code implicitly assumes is: `bytes verified by HMAC == bytes that determine shop/topic identity`. In reality: `bytes verified by HMAC (raw_body only) != bytes used for shop/topic attribution (shop-domain/topic headers)`. Because the shop and topic headers are excluded from `to_signable_string`, any request carrying a previously-valid `(raw_body, hmac)` pair — obtained from any legitimately delivered webhook for the app (e.g. one sent to the attacker's own installed shop) — will still pass `HmacValidator.validate` even if the `x-shopify-shop-domain` and/or `x-shopify-topic` headers are swapped to arbitrary values. This lets an attacker replay a genuine webhook body/HMAC pair while re-labeling it as belonging to a different (victim) shop or a different topic.

### Impact Explanation
This breaks the tenant-identity binding the gem is relying on to route/attribute webhook data: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built entirely from unauthenticated header values, while only the body bytes were cryptographically verified. An app that persists or acts on webhook data keyed by `shop`/`topic` (the intended usage pattern, per `Registry.process`) can be made to attribute a captured, validly-signed payload to a different shop or a different topic than the one it actually originated from — a cross-tenant confusion primitive that satisfies the Critical "cross-tenant access" impact category.

### Likelihood Explanation
An attacker only needs a single legitimately delivered webhook (body + HMAC header) for the target app — trivially obtainable by installing the app on their own store, which requires no access to `client_secret`/`api_secret_key`. They then replay that exact raw body and HMAC while altering the `shop-domain`/`topic` headers on the request delivered to the app's webhook endpoint. No secret material, privileged account, or TLS interception is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them to the signed payload), so that `HmacValidator.validate` fails if any of these identity-bearing headers are altered relative to the signed content.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; trigger any webhook event so Shopify delivers a legitimate `POST` with body `B`, `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Capture `(B, H)`.
3. Send a new request to the app's webhook endpoint with the same body `B` and `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-hmac-sha256" => H, ...})` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `B` against `H`.
5. `Registry.process` calls the handler with `shop: "victim.myshopify.com"`, causing the app to process attacker-controlled webhook content under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
