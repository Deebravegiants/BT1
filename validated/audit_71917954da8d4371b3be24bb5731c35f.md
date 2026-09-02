### Title
Webhook HMAC only signs the request body, not the `shop-domain` header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` uses that same body-only HMAC to authenticate the whole webhook, then trusts `request.shop` (from the `x-shopify-shop-domain`/`shopify-shop-domain` header) when dispatching to the handler. Because the shop identity is never part of the signed material, any party who can obtain one validly-signed `(body, hmac)` pair for the shared app secret can replay it with an arbitrary `shop-domain` header and have it processed as if it originated from a different, unrelated shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values are all read straight from HTTP headers and are never included in the signed string: [2](#0-1) 

`Registry.process` validates only this body-bound HMAC and then dispatches the handler using the unauthenticated `request.shop` value: [3](#0-2) 

`HmacValidator.validate` simply recomputes the HMAC over `verifiable_query.to_signable_string` (the body) with the app's shared `api_secret_key` and compares it to the supplied `hmac`: [4](#0-3) 

Because `api_secret_key` is a single secret shared by the app across **all** installed shops (not a per-shop secret), any tenant that has installed the app can obtain a validly HMAC-signed `(body, hmac)` pair (e.g., by triggering any webhook event on their own store) and then send that exact `body` + `hmac` to the app's webhook endpoint while substituting a different value in the `shop-domain` header. The equality the code implicitly assumes but does not enforce is:

`shop_that_produced_the_signed_body == shop_header_used_to_attribute_the_webhook`

Since the header is not covered by the HMAC, an attacker fully controls the right-hand side while the left-hand side is unconstrained — the two are never actually checked against each other.

### Impact Explanation
This breaks a tenant-identity binding: the webhook handler processes attacker-supplied data (`request.parsed_body`) while attributing it to a `shop` of the attacker's choosing via `WebhookMetadata.new(topic:, shop:, body:, ...)`: [5](#0-4) 
A malicious merchant (an "unprivileged" party relative to other tenants of the same app) can cause the host application to act on a victim shop's behalf — e.g., writing/updating data keyed by `shop`, revoking/enabling app-side entitlements, or triggering shop-scoped side effects for a shop the attacker does not own. This is a cross-tenant access issue enabled purely by this gem's webhook verification not binding shop identity into the HMAC-checked material.

### Likelihood Explanation
Any developer/merchant who has legitimately installed the app can generate valid `(body, hmac)` pairs for arbitrary topics by simply performing normal actions on their own store (e.g., creating an order fires `orders/create`). Replaying that exact payload to the app's public webhook endpoint with a forged `shop-domain` header requires no secret knowledge and no privileged access — only the ability to send HTTP requests, which satisfies the "unprivileged internet user" threat model.

### Recommendation
Include the shop-identifying header(s) (and ideally topic/webhook-id) in the signed material that `HmacValidator` checks, or otherwise cryptographically bind `request.shop` to the verified payload before it is passed to `WebhookMetadata`/handlers. At minimum, downstream consumers of `WebhookMetadata#shop` should be documented as receiving an unauthenticated value, and the registry should not treat it as trusted tenant attribution without additional verification (e.g., looking up whether the `webhook_id` returned actually belongs to that shop before dispatch).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g., `orders/create`), capturing the raw request body `B` and its `x-shopify-hmac-sha256` header `H`. `H` is valid because `HmacValidator.compute_signature` uses the single app-wide `api_secret_key`.
2. Attacker sends a POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256`: `H` (unchanged, still valid since it only covers `B`)
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic`: unchanged or attacker-chosen registered topic
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host application to process attacker-controlled data as if it came from the victim shop.

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
