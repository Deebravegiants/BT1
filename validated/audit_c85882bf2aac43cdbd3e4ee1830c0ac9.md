Based on my investigation, I found a genuine identity-binding break analogous to the reported bug class.

### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted for tenant routing but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the shop, topic, and webhook-id used to route and process the webhook are taken from unauthenticated HTTP headers. This breaks the identity binding "shop authenticated == shop acted upon."

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively, and `Request#hmac` reads the `hmac-sha256`/`x-shopify-hmac-sha256` header value that is checked against that raw body only: [1](#0-0) [2](#0-1) 

The `shop`, `topic`, and `webhook_id` fields, however, are pulled straight from separate HTTP headers that are never mixed into the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (the raw body) and compares it against the secret-keyed HMAC — it never touches `shop`, `topic`, or `webhook_id`: [4](#0-3) 

After that check passes, `Registry.process` builds `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id` verbatim — i.e., the tenant identity dispatched to the app's handler is the unauthenticated header value, not something proven by the signature: [5](#0-4) 

Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-tenant secret), any party that can obtain one validly-signed webhook body (e.g., from their own installed/test shop, or a body with predictable/replayable content) can replay it with the `shop-domain` header rewritten to a victim shop's domain. The HMAC will still validate, because it only ever certifies the bytes of `@raw_body`, and `Registry.process` will hand the forged shop identity straight to the app's webhook handler.

### Impact Explanation
This is a cross-tenant identity-binding failure: `shop (authenticated by HMAC) != shop (acted upon by the handler)`. Any app relying on `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) to select the tenant record to mutate — for example, mandatory compliance topics like `shop/redact`, `customers/redact`, or `customers/data_request`, or app-specific deprovisioning logic on `app/uninstalled` — can be tricked into performing that tenant-scoped action against a shop the attacker does not control, using only a validly-signed body obtainable from any shop (including one the attacker legitimately owns).

### Likelihood Explanation
Likelihood is high for any topic whose body content is static, predictable, or attacker-controllable (e.g., an app-defined webhook whose payload the attacker can also trigger on their own store), since the attacker only needs one genuine `(body, hmac)` pair from a store they control and then need only swap the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header before delivering the request to the app's webhook endpoint.

### Recommendation
Bind the signature to the tenant and message identity, not just the body: include `shop`, `topic`, and `webhook_id` in the value passed to `to_signable_string` (or independently verify/derive the shop from a source Shopify itself certifies, and refuse processing if the header-declared shop cannot be tied to the signed payload). Concretely:

```diff
- sig { override.returns(String) }
- def to_signable_string
-   @raw_body
- end
+ sig { override.returns(String) }
+ def to_signable_string
+   "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
+ end
```

### Proof of Concept
1. Install (or register a test webhook for) a shop `attacker.myshopify.com` that the attacker controls, and capture a legitimately delivered webhook: headers `x-shopify-topic`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-webhook-id`, plus the raw body `B`.
2. Because `HmacValidator.validate` only recomputes the HMAC over `B` (see `to_signable_string` returning `@raw_body`), the captured `x-shopify-hmac-sha256` value remains valid for `B` regardless of any other header.
3. Replay the request to the app's webhook endpoint, replacing `x-shopify-shop-domain` with `victim.myshopify.com` (and, if desired, `x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against the secret, then invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the app to execute the shop-scoped webhook logic against `victim.myshopify.com` instead of the shop that actually sent it.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
