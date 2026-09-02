### Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes `to_signable_string` from only the raw request body, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers. Since the app's webhook HMAC secret (`api_secret_key`) is shared across every shop that has installed the app, any tenant that receives a legitimate webhook can replay the same body+HMAC pair with a forged `shop-domain` header, and `Registry.process` will accept it and dispatch it to the handler as if it originated from a different (victim) shop.

### Finding Description
The signing/verification binding is:

`computed_hmac = HMAC(api_secret_key, raw_body)` (does not include `shop`, `topic`, or `webhook_id`)

but the trust decision made by `Registry.process` is:

`if valid_hmac(raw_body) then trust(shop_header, topic_header, webhook_id_header)`

This breaks the equality that should hold: `authenticated_field == acted_on_field`. The HMAC authenticates the body bytes only, yet the shop identity used to route/act on the webhook (`request.shop`) is taken straight from a header that is never covered by that signature: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` verifies exactly this `to_signable_string` (the raw body) against the secret, and nothing else: [3](#0-2) 

`Registry.process` then trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler, based solely on that body-only HMAC check: [4](#0-3) 

Because the same `api_secret_key` is used to sign webhooks for every shop that installs the app, an attacker who controls one installed shop (a normal, unprivileged merchant of a multi-tenant app — not requiring the app's `client_secret` or any elevated access) can:
1. Trigger or capture a legitimate webhook delivery to their own shop (body + valid `x-shopify-hmac-sha256`).
2. Replay that exact body/HMAC pair to the app's webhook endpoint, substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still returns `true` (only the body is checked), and `Registry.process` dispatches the payload to the handler tagged with the victim shop, causing the host application to process/attribute data under the wrong tenant.

### Impact Explanation
This crosses a tenant boundary using only artifacts an ordinary merchant already possesses (a valid webhook delivered to their own installation), matching the Critical "cross-tenant access" category: the library-level primitive that host applications rely on to attribute webhook data to a shop (`request.shop`) is not cryptographically bound to the same bytes that were HMAC-verified.

### Likelihood Explanation
Likelihood is moderate-to-high in any multi-tenant app: no secret material beyond what an installed merchant already legitimately triggers is required, only the ability to capture/replay one's own webhook HTTP request and edit a header, then send it to the app's public webhook endpoint.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable payload used for validation (or cryptographically bind them to the body, e.g. by concatenating them into `to_signable_string` and re-verifying), so that `HmacValidator.validate` fails if any of these headers are altered independently of the signed body. At minimum, document and/or enforce that consumers cannot rely on `request.shop`/`request.topic` without additional shop allow-listing, since the current HMAC only protects body integrity, not header authenticity.

### Proof of Concept
1. App installs on Shop A (attacker-controlled) and Shop B (victim) with the same `api_secret_key`.
2. Shopify sends a legitimate webhook to the app for Shop A: body `{"id":1}` with header `x-shopify-shop-domain: shop-a.myshopify.com` and a valid `x-shopify-hmac-sha256`.
3. Attacker replays this exact body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header; `Utils::HmacValidator.validate` computes the HMAC over `@raw_body` only and it matches, so `Registry.process` invokes the handler with `shop: "shop-b.myshopify.com"`, even though the payload never originated from or was authorized by Shop B.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
