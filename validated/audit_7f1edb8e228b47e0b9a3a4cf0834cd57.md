### Title
Webhook `shop` (and topic/api-version/webhook-id) identity fields are not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by application handlers to attribute the webhook to a specific merchant are taken from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC via `HmacValidator.validate`, which only proves the raw body bytes were signed by `Context.api_secret_key` — it says nothing about which shop the header claims to be: [3](#0-2) [4](#0-3) 

The identity binding broken here is: `hmac_signed_bytes == raw_body` while `tenant_identity_used_by_handler == header("shop-domain")`. Since the app's `client_secret` (used to compute the HMAC) is shared across every shop that installs the app, any attacker who controls a store with the app installed can obtain a legitimately-signed `(raw_body, hmac)` pair (e.g., by triggering a webhook from their own shop with body content they crafted through normal actions like naming a product/order field). They can then replay that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will dispatch the handler with `WebhookMetadata.new(shop: request.shop, ...)` claiming to be the victim shop: [5](#0-4) 

Any handler logic that keys off `data.shop` (e.g., looking up the victim's session/access token, writing tenant-scoped records, or triggering shop-specific side effects) will act on attacker-controlled body content under the victim's identity.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is meant to enforce: an unprivileged attacker who only has their own shop's installation can cause the app to process forged webhook data attributed to a different, unrelated merchant (cross-tenant access/injection). Depending on how the consuming app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to fetch the victim's stored session/access token and issue further API calls, or to write into the victim's tenant record), this can escalate to acting with another merchant's credentials or corrupting another merchant's data — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Medium-High. The attacker only needs their own store with the target app installed (no privileged account or leaked secret required), the ability to trigger a webhook with a body of their choosing (readily achievable through normal shop actions that populate webhook payload fields), and the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint (no TLS interception or credential compromise needed). This is a design property of the gem's `Request`/`HmacValidator` pair, not a host-application misuse, since `to_signable_string` for `Request` is hardcoded to the body only and the header-derived `shop`/`topic` are otherwise treated as authenticated data by `Registry.process`.

### Recommendation
Extend `Request#to_signable_string` (or add a secondary check in `Registry.process`) to bind the header-derived identity fields (`shop`, `topic`, `webhook_id`) into the verified material, or otherwise cross-validate `request.shop` against a value independently known to the app (e.g., an active session/shop list) before dispatching to handlers. At minimum, document prominently that `shop`/`topic`/`webhook_id` headers are NOT covered by the HMAC and must not be trusted by handlers without independent verification.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a real webhook (e.g. `orders/create`) with a body containing attacker-chosen field values.
2. Capture the resulting `x-shopify-hmac-sha256` header and raw JSON body — this is a validly signed `(body, hmac)` pair for the app's `client_secret`.
3. Replay a POST to the app's webhook endpoint using the same body and hmac, but set `x-shopify-shop-domain: victim.myshopify.com` (and desired `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the secret [6](#0-5) , then invokes the handler with `shop: "victim.myshopify.com"` and the attacker-controlled body [5](#0-4) .

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
