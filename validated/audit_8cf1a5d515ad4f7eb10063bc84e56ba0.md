I have enough information to finalize the analysis.

### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values consumed by the app come from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
but `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read straight from HTTP headers, independent of the signed body: [2](#0-1) 

`Registry.process` validates the HMAC over that signable string only, then immediately trusts the header-derived `shop`/`topic`/`api_version`/`webhook_id` values to build `WebhookMetadata` and dispatch it to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms this — it only ever calls `verifiable_query.to_signable_string`, never inspecting headers such as `shop-domain` or `topic`: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated (via HMAC) == shop consumed by the app handler`. In reality, the HMAC only binds the **body**; the `shop-domain` header used to route/attribute the webhook to a specific merchant is not part of the signed payload at all. An unprivileged party who legitimately receives webhooks for their own shop (e.g., any Shopify merchant installing the app) can capture one such Shopify-signed request and resend it to the app's webhook endpoint with a **different** `x-shopify-shop-domain` (and/or `x-shopify-topic`) header while leaving the body and its HMAC untouched. Because `HmacValidator.validate` only checks the body against the secret, the tampered request still passes signature verification, and the app processes the payload attributing it to whatever shop domain the attacker put in the header.

### Impact Explanation
This is a cross-tenant identity-binding bypass at the shop level: an app that persists webhook data keyed by `WebhookMetadata#shop` (as the SDK's own documented pattern — `data.shop` — instructs consumers to do) can be made to store or act on a legitimately-signed payload under an arbitrary victim shop domain, without ever possessing that shop's credentials. This matches the "shop authenticated versus the shop stored/consumed" identity-binding class called out in scope, and corresponds to cross-tenant access, which is rated Critical impact.

### Likelihood Explanation
Any Shopify merchant/dev store owner who has legitimately installed the app can trivially obtain one Shopify-signed webhook for their own shop (webhooks are delivered to the app's public endpoint) and replay it with a modified `shop-domain`/`topic` header, since no additional secret knowledge is required — only the ability to send an HTTP request to the app's public webhook endpoint, which is unauthenticated by design and relies solely on this gem's HMAC check.

### Recommendation
Include the `shop-domain`, `topic`, `api_version`, and `webhook_id` header values in the HMAC-signable string (or otherwise cryptographically bind them to the body verification), so that tampering with any of these headers invalidates the signature, matching Shopify's guidance that the full raw payload used for HMAC verification must be the exact bytes Shopify sent, and that any values used to route/attribute the webhook should be bound to that verified payload.

### Proof of Concept
1. Legitimate shop A installs the app; Shopify sends a webhook POST to the app's endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`, and some JSON body.
2. Attacker (who is shop A's merchant, or anyone able to capture/replay this HTTP request) resends the identical body and HMAC header, but changes `x-shopify-shop-domain` to `shop-victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and finds it matches — validation succeeds despite the header tampering: [5](#0-4) 
4. The app's `WebhookHandler#handle` receives `WebhookMetadata` with `shop: "shop-victim.myshopify.com"` and processes/stores the order data as if it belonged to the victim shop.

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
