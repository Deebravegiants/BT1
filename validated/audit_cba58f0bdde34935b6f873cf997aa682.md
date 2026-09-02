### Title
Webhook `shop` (and `topic`) identity is not covered by the HMAC signature, allowing shop-domain spoofing / cross-tenant webhook delivery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook purely by verifying an HMAC over the raw request body, but the `shop` and `topic` values that are handed to the app's handler as the tenant/event identity come from unauthenticated HTTP headers that are never part of the signed payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate_signature` computes/compares the signature solely against that signable string [2](#0-1) . Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.) with no cryptographic binding to those headers [3](#0-2) .

`Registry.process` validates the HMAC and then trusts `request.shop`/`request.topic` as the tenant/event identity that is forwarded to the app's handler via `WebhookMetadata` [4](#0-3) .

This breaks the intended identity binding: `HMAC-verified bytes == request body` but `tenant/topic identity == unauthenticated header value`, i.e. `signed(body) ≠ signed(shop, topic)`. Any party capable of obtaining one validly-signed webhook body (e.g., from their own development/test store, which they legitimately control) can replay that exact same body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and/or `x-shopify-topic` header) for a victim shop. The HMAC check still passes because it only verifies the body bytes, but the handler executes believing the data belongs to the victim shop and topic.

### Impact Explanation
This is a cross-tenant identity confusion in webhook processing: an app relying on `WebhookMetadata#shop` to select or scope which tenant's data to update (a very common pattern, e.g. `shop/redact`, `orders/create`, `app/uninstalled`) can be made to act on an attacker-chosen shop domain using a signature the attacker legitimately obtained for different content. Depending on the host application's handler logic, this can lead to writing/deleting data attributed to a shop that never sent the webhook, or triggering privileged actions (like `app/uninstalled` cleanup or `shop/redact`) for a victim shop, which is a cross-tenant access weakness.

### Likelihood Explanation
Exploitation requires the attacker to have access to at least one legitimately HMAC-signed webhook body (readily achievable by installing the app on their own store) and the ability to POST arbitrary headers to the app's public webhook endpoint, which any unprivileged internet user can do since webhook endpoints are unauthenticated HTTP endpoints by design. No `api_secret_key`, access token, or privileged credentials are required.

### Recommendation
Include the shop domain (and topic) in the HMAC-verified material, or otherwise cryptographically bind them to the signed payload, e.g. by validating that the `shop` returned from `Request#shop` matches an expected/known shop for that HMAC context, or by having `to_signable_string` incorporate the shop/topic headers so tampering with them invalidates the signature. At minimum, document and enforce that consumers of `WebhookMetadata#shop` must independently confirm the shop is one they have an active session/installation for before trusting it as the tenant identity.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and captures a legitimately delivered webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), `x-shopify-topic: orders/create`.
2. Attacker sends a POST to the app's webhook endpoint with the exact same raw body `B` and HMAC header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally changes `x-shopify-topic`).
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [5](#0-4) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: parsed_body, ...)` [6](#0-5) , causing the app to process attacker-controlled data under the victim shop's identity.

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
