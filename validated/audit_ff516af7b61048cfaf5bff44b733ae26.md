Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop`, `topic`, and `webhook_id` are all read straight from unauthenticated HTTP headers via `shopify_header` (`lib/shopify_api/webhooks/request.rb:15-33`, `67-70`) and are never included in the HMAC-signed payload. `Registry.process` validates only `Utils::HmacValidator.validate(request)` (`lib/shopify_api/webhooks/registry.rb:190`), which calls `to_signable_string` → body only, then dispatches `handler.handle` using `request.shop` and `request.topic` taken from those unsigned headers (`lib/shopify_api/webhooks/registry.rb:198-199`).

### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, but the `shop`, `topic`, and `webhook_id` values that the host application uses to attribute and dispatch the webhook are taken from HTTP headers that are never part of that signed string. This breaks the identity binding: bytes verified (raw body) ≠ bytes acted on (headers used to tag which shop/topic the payload belongs to).

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors pull directly from the incoming HTTP headers with no cryptographic linkage to the HMAC [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string`, i.e., the body [3](#0-2) . `Registry.process` gates on this HMAC check and then builds `WebhookMetadata` using `request.shop` and `request.topic`—both unauthenticated header values—handing them to the app's registered handler [4](#0-3) .

Because the webhook endpoint is a public HTTP endpoint by design (Shopify calls it over the internet), any unprivileged internet user who can obtain one valid `(raw_body, hmac)` pair — e.g., by installing the app for their own shop and capturing a legitimately delivered webhook — can replay that exact body/HMAC while freely substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers. The signature check still passes because those headers were never part of the signed content, so the handler processes attacker-controlled body content under an arbitrary shop or topic identity of the attacker's choosing.

### Impact Explanation
This crosses a tenant boundary: `WebhookMetadata.shop` is the value host applications typically use as the key to look up or write per-merchant records (order/product/customer data, GDPR redaction handlers such as `shop/redact` and `customers/redact`, etc.). An attacker can cause the app to process a captured, validly-signed payload under a `shop` value naming a different (victim) tenant, or under a different `topic` than the one that was actually signed (e.g., turning a benign event into a `customers/redact` or `shop/redact` trigger for a victim shop). This matches "cross-tenant access" impact.

### Likelihood Explanation
Requires only: (1) the ability to send an arbitrary HTTP request to the app's public webhook endpoint, which is inherent to how webhook endpoints must be exposed, and (2) possession of one legitimately-signed `(body, hmac)` pair, obtainable by any user who can trigger a webhook for their own store (e.g., install the app, or trigger any subscribed webhook topic on their own shop). No `api_secret_key`, access token, or privileged account is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the body), rather than only signing the raw body while trusting these identity/routing fields from unauthenticated headers. At minimum, `Request#to_signable_string` should incorporate the shop-domain and topic headers so a replayed body cannot be relabeled to a different shop or event type.

### Proof of Concept
1. Attacker registers the app for their own shop `attacker.myshopify.com` and subscribes to a webhook topic.
2. Shopify delivers a legitimately signed webhook: headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`, plus `raw_body`.
3. Attacker resends the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com` and/or `X-Shopify-Topic` to `customers/redact`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` still returns `true` because it only checks the raw body against the signature [5](#0-4) .
5. `Registry.process` invokes the registered handler with `shop: "victim.myshopify.com"`, `topic: "customers/redact"`, and the attacker's chosen body content [6](#0-5) , causing the host app to act on victim-tenant data using attacker-supplied content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
