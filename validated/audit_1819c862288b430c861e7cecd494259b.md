### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while the HMAC only signs the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload as just the raw HTTP body, but exposes `shop`, `topic`, and `webhook_id` as separate accessors read straight from HTTP headers that are never included in that signed payload. `Registry.process` verifies only the body's HMAC and then hands the header-derived `shop` value to the handler as the tenant identifier, so the field the application uses to bind a webhook to a specific merchant is never cryptographically bound to the signature that "authenticates" the request.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are all read from headers, independent of the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` gates on this HMAC check and then forwards the *header-derived* `request.shop` (and `request.topic`, `request.webhook_id`) to the handler as the authoritative tenant/topic identity for the webhook: [4](#0-3) 

The identity binding broken is: **shop authenticated (implicitly, by a valid body HMAC) ≠ shop delivered to the handler as the session/tenant key**. Because `shop-domain`, `topic`, and `webhook-id` headers are not part of `to_signable_string`, they can be modified by anyone relaying the HTTP request to the app's webhook endpoint without invalidating the HMAC signature, since the signature check only verifies the body bytes were produced with the app's `api_secret_key` at some point - it says nothing about which shop or topic that body was originally sent for.

### Impact Explanation
An unprivileged internet user who is a genuine merchant of a shop with the app installed (or who otherwise obtains one valid `(raw_body, hmac)` pair for *any* topic, e.g., by capturing their own shop's real webhook deliveries) can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) with a different, victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, so `Registry.process` dispatches the handler with `shop: <victim-shop>` and attacker-controlled body content. Any host application logic that keys per-tenant state (sessions, database records, business actions) off `WebhookMetadata#shop` as returned by this gem will process attacker-supplied data under the wrong tenant identity - a cross-tenant confusion/impersonation at the webhook-processing layer.

### Likelihood Explanation
Likelihood is limited by the fact that the attacker needs at least one legitimately-signed `(body, hmac)` pair, which they can obtain by being a real (even free/trial) merchant of the app and receiving one genuine webhook, or by controlling any shop that triggers a webhook with attacker-influenced body content. No secret material is required to reuse the pair against a different shop identity, since only the header is manipulated.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` values into the HMAC-signed payload verification (Shopify webhook delivery includes these values in the request context that the app should independently verify came from Shopify for that specific shop, e.g., by matching against the shop the webhook was registered for), or require the consuming application to cross-check `request.shop` against a shop that is otherwise trusted (e.g., a shop with an active, verified session/registration), rather than treating the header-derived shop as authenticated purely because the body's HMAC validated.

### Proof of Concept
1. Attacker's own shop `attacker-shop.myshopify.com` has the app installed and receives a real webhook: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical HTTP request to the app's webhook endpoint but changes only the header: `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (body `B` and its HMAC header untouched).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates `HMAC(secret, B)` against the unchanged `hmac` header - this still passes because `to_signable_string` never included the shop header: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, i.e., attacker-controlled body content is delivered tagged as belonging to `victim-shop`.

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
