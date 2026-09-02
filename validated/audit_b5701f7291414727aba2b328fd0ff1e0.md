### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook relabeling - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook using `Utils::HmacValidator.validate(request)`, but that validator only signs/verifies the raw request body. The `shop` (and `topic`/`webhook_id`) values that the handler receives and acts on come from unauthenticated HTTP headers that are never part of the signed bytes. An attacker who legitimately receives one valid, HMAC-signed webhook (e.g. by installing the app on their own shop) can replay that exact body/HMAC pair while swapping the `x-shopify-shop-domain` header to a victim shop, and the gem will accept it as authentic and hand it to the handler labeled as belonging to the victim shop.

### Finding Description
`HmacValidator.validate` computes and compares the signature only over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw HTTP body — none of the Shopify headers are included: [2](#0-1) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from client-supplied HTTP headers with no cryptographic binding to the body that was actually signed: [3](#0-2) 

`Registry.process` validates only the HMAC and then dispatches the handler using `request.shop` (and other header-derived fields) as if they were authenticated: [4](#0-3) 

This breaks the identity binding: `shop` authenticated by the HMAC (none — the HMAC covers only the body) ≠ `shop` used by the handler to act on the tenant (`request.shop`, taken from an unauthenticated header). Since the same `api_secret_key` is used to validate webhooks for the app regardless of which shop sent them, any party who can obtain one legitimately-signed webhook (trivially achievable by installing the app on a shop the attacker controls, or observing any exposed webhook payload/HMAC pair) can resend that exact body+HMAC to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a different shop. `HmacValidator.validate` will pass because it never inspected the header, and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: a handler that persists or acts on webhook data keyed by `shop` (the normal, documented usage pattern — see `WebhookMetadata.new(topic:, shop:, body:, ...)`) can be tricked into writing or acting on another merchant's tenant record using attacker-supplied body data. This matches the Critical "cross-tenant access" impact category, since a webhook (potentially carrying customer/order/inventory data or replay-triggered side effects) can be attributed to any target shop known to the attacker, without ever knowing the target's data or credentials.

### Likelihood Explanation
Exploitation requires no privileged credentials from the target: an attacker needs only (a) their own trial install of the vulnerable app to harvest one valid `(body, hmac)` pair from a real webhook delivery, and (b) the ability to POST to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header, which this library does nothing to authenticate. The library exposes and encourages exactly this trust model via `WebhookMetadata`, so any app author following the documented pattern of trusting `shop` in the handler is affected.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify them against a lookup keyed only by the signature, or require the handler to independently confirm the `shop` is the one the webhook subscription was registered for). At minimum, document clearly that `request.shop`/`topic`/`webhook_id` are unauthenticated and must not be trusted for tenant-scoping decisions unless independently verified.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com`; Shopify sends a real webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(B, secret)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body `B` and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC(B, secret)` (per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31) and it matches, since only `B` is signed.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-200) invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, even though that body was never issued for the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
