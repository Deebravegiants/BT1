Confirmed the root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac`, `topic`, `shop`, `api_version`, and `webhook_id` are all read from unauthenticated HTTP headers, none of which are included in the HMAC-signed content.### Title
Webhook `shop`, `topic`, `api_version`, and `webhook_id` fields are trusted for cross-tenant routing but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from raw HTTP headers, but `to_signable_string` only returns `@raw_body`. The HMAC validation performed by `Registry.process` therefore only authenticates the body bytes — it never binds the `shop` (tenant identity) header to the signature, even though that header value is passed straight into the app's webhook handler as trusted tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 
returning only the raw body. `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` — i.e., only the body is HMAC-checked: [2](#0-1) [3](#0-2) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are read straight from attacker-controllable HTTP headers with no cryptographic binding to the signature: [4](#0-3) 

These header values are then passed as trusted tenant/topic identity into the host app's handler: [5](#0-4) [6](#0-5) 

The identity binding broken here is: `hmac_signature ≡ HMAC(secret, raw_body)` while the tenant-identifying claim `shop` (and `topic`/`webhook_id`) are never part of the signed content, i.e. `shop_used_by_handler ≠ shop_bound_by_hmac`.

### Impact Explanation
An unprivileged attacker who owns any Shopify store enrolled with the same app (or who otherwise obtains one valid `raw_body` + `hmac` pair legitimately delivered for their own shop, e.g. through their own webhook subscription with content they can trigger, such as an empty-body topic) can replay that exact signed body to the victim app's webhook endpoint while altering the `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header. Because none of these fields participate in the HMAC computation, the signature still validates, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen (victim's) shop domain and/or an attacker-chosen topic/webhook_id, while the actual `body` content is whatever the attacker controls from their own account. This crosses the tenant boundary: data attributed to one shop is processed as belonging to another, enabling cross-tenant data confusion/injection in any host application that trusts `WebhookMetadata#shop`/`#topic` without independent verification (e.g., session lookup keyed only by that value). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is limited by the attacker needing at least one genuine HMAC-signed webhook body from Shopify (trivially obtainable by installing/using the app on their own store and triggering any webhook, including trivial empty-body topics like `shop/redact`), then replaying it with modified headers to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or TLS interception is required — only normal use of the app as an installed merchant and control over the HTTP request sent to the app's own webhook receiver.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed content, or otherwise cryptographically bind them to the signature (e.g., compute the signature over a canonicalized string of `shop|topic|webhook_id|raw_body` on both signer and verifier, if Shopify's webhook signing scheme supports this) so that tampering with these headers invalidates the signature. At minimum, host-app-facing documentation should explicitly warn that `WebhookMetadata#shop`/`#topic` are NOT covered by the HMAC and must not be used as the sole tenant-routing key without additional verification (e.g., cross-checking against a known/registered shop list).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook for topic `shop/redact` with empty body `{}` and a valid `shopify-hmac-sha256` header computed over `"{}"`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint reusing the exact `raw_body: "{}"` and the exact `shopify-hmac-sha256` value, but changes `shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (`"{}"`only) and it matches, per [1](#0-0)  and [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", ...)`, per [5](#0-4) , causing the host app to process a mandatory-compliance webhook (or any other replayable topic) as if it originated from the victim shop, despite `shop` never having been part of the signed payload.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
