I have sufficient evidence to write up the finding now.

### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken directly from HTTP headers to build the `WebhookMetadata` that is handed to the app's handler. Those header-derived identity fields are never included in the signed bytes, so they can be freely substituted by anyone who can produce (or replay) a `(body, hmac)` pair, breaking the binding `shop authenticated == shop the handler acts on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

None of `topic`, `shop`, `api_version`, or `webhook_id` — all read straight from HTTP headers — are part of the signed string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` and therefore only checks the body bytes, then immediately trusts `request.shop`/`request.topic` (sourced from headers) to build `WebhookMetadata` passed to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(... , verifiable_query.to_signable_string)` and compares it to the `hmac` field of the same object — it has no notion of headers at all: [4](#0-3) 

Because the HMAC only binds the JSON body, the equality that should hold — *the shop that produced the signed bytes* == *the shop the SDK reports to the handler* — is not enforced. An unprivileged actor who legitimately operates any Shopify store that has the target app installed (e.g., a free development store) can trigger a real webhook and capture a valid `(raw_body, hmac)` pair signed with the app's own secret. That pair remains cryptographically valid no matter what `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers accompany it, because none of those headers are part of the signed content. The attacker can then replay that exact body to the app's single shared public webhook endpoint with the `shop-domain` header rewritten to a victim shop, and/or the `topic` header rewritten to a different topic than the one that was actually fired. `Registry.process` will accept the HMAC as valid and dispatch `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` — both attacker-controlled — to the registered handler.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` (or `#topic`) to key data, authorize an action, or select which merchant's records to mutate will act on a shop it never received the corresponding event from. This is a cross-tenant identity-binding break: data belonging to shop B can be attributed to, or overwritten under, shop A's identity purely by an attacker who controls any store with the target app installed, satisfying the "cross-tenant access" impact category through a credential/identity boundary the SDK is documented to guarantee (webhook HMAC = proof of authenticity for the accompanying metadata).

### Likelihood Explanation
Webhook endpoints are public HTTP(S) endpoints reachable by anyone; the only "privilege" required is the ability to install the app on some (even free/trial) store to capture one legitimate `(body, hmac)` pair, which is available to any unprivileged internet user. No access token, `api_secret_key`, or interception of another tenant's traffic is required.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., verify `shop` against session/tenant records established independently of the header, and reject bodies whose header-declared topic doesn't match content expectations). At minimum, document that `WebhookMetadata#shop`/`#topic` are unauthenticated and must not be trusted for tenant-sensitive dispatch without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on Shop A (a store they control) and triggers an event (e.g. `orders/create`) so the app's webhook endpoint receives a legitimate request with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker resends an HTTP POST to the same public webhook endpoint with body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (Shop B, a victim) instead of Shop A's domain.
3. `ShopifyAPI::Webhooks::Request.new` parses the spoofed headers; `Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and finds it matches `H` — validation succeeds.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", topic: ..., body: B, ...)`, so the app processes event `B` as if it belonged to Shop B, even though Shop B never sent it.

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
