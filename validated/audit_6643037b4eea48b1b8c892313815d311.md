### Title
Webhook `shop` and `topic` identity not bound to HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC before dispatching the (unverified) `shop`/`topic` to the app's handler, breaking the binding `hmac_signed_bytes == identity_fields_used`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from caller-supplied headers with no cryptographic tie to the HMAC: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which in turn calls `to_signable_string` (i.e., only the raw body bytes) and compares it against the `hmac-sha256` header: [3](#0-2) [4](#0-3) 

Because the signature covers only the body, `shop`, `topic`, `webhook_id`, and `api_version` are never authenticated. Once any attacker obtains one legitimate `(raw_body, hmac)` pair for a given app (e.g. from their own installed shop, which they legitimately receive), they can resend that exact body with the same valid HMAC to the app's shared webhook endpoint while freely rewriting `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers. The forged request still passes `HmacValidator.validate`, and `Registry.process` will hand the attacker-chosen `shop` and `topic` straight to the registered handler: [5](#0-4) 

This equality that should hold — `authenticated_shop == shop_acted_on_by_handler` — is broken: the HMAC authenticates bytes, but the shop identity used to route/act on data is taken from an unauthenticated header.

### Impact Explanation
Host applications rely on `WebhookMetadata#shop` (and `#topic`) as the trusted tenant identifier once `Registry.process` succeeds, since the gem's documented contract is "HMAC valid ⇒ this webhook genuinely originates from `shop`." An attacker who legitimately controls one shop with the app installed can spoof webhooks appearing to originate from any other shop (cross-tenant), or redirect a captured body to a different topic handler than the one it was actually issued for (topic confusion), causing the host app to process/store data under the wrong merchant's account. This meets the "cross-tenant access" High/Critical impact bar because the merchant/topic identity binding is broken purely via a crafted HTTP header, without the app's `client_secret` or a token.

### Likelihood Explanation
Any user who can get the app installed on a shop (even a low-value or trial shop) can capture a valid `(raw_body, hmac)` webhook pair sent to their own endpoint, then replay it to the target app's shared webhook endpoint with modified `shop`/`topic` headers — no secret material or privileged access is required beyond running one's own shop through normal signup.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed payload (or otherwise cryptographically bind them, mirroring how `AuthQuery#to_signable_string` binds `code`, `host`, `shop`, `state`, `timestamp`), so that `HmacValidator.validate` fails if any of these values are altered from what was actually signed by Shopify.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a genuine webhook: body `{"id":1}`, header `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `victim-shop.myshopify.com` while `to_signable_string` is unchanged (`{"id":1}`), so `Utils::HmacValidator.validate` still passes: [6](#0-5) 
4. `handler.handle` is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", ...)`, causing the host app to act as if this webhook genuinely originated from `victim-shop`.

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
