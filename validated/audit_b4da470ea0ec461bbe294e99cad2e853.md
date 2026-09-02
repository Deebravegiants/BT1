### Title
Webhook `shop` (and `topic`/`webhook_id`) fields are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so `Utils::HmacValidator.validate` authenticates the payload bytes but never binds the `x-shopify-shop-domain` (or `x-shopify-topic`/`x-shopify-webhook-id`) header to that signature. `Registry.process` nevertheless uses `request.shop` as the tenant identifier passed into the app's webhook handler, creating an identity binding break identical in class to the TON report's pattern of acting on data that was not validated by the integrity check that gated processing.

### Finding Description
`Registry.process` is the sole gate for webhook authenticity: [1](#0-0) 

It calls `Utils::HmacValidator.validate(request)`, which computes the HMAC exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers, which are never part of the signed material: [4](#0-3) 

After the HMAC check passes, `Registry.process` builds `WebhookMetadata` using this unauthenticated `request.shop` value and hands it to the merchant app's handler as the tenant identity for the event: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `shop header used to route/attribute the event == shop bytes covered by the verified HMAC`. Because the HMAC only covers `@raw_body`, this equality never holds — the `shop` (and `topic`/`webhook_id`) fields are "acted on but not covered by the HMAC," matching the exact bug class called out in scope.

### Impact Explanation
Any actor who possesses one genuinely-signed webhook body+HMAC pair for an app that shares a single `client_secret` across multiple shops (a standard, documented Shopify app topology) can replay that same body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header. `Utils::HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain. Any handler logic that uses `data.shop` to look up a session/token, write per-shop state, or make authorization decisions (a standard integration pattern, since this is precisely the value the gem exposes for that purpose) will attribute attacker-controlled data or attacker-controlled events to a victim tenant — a cross-tenant integrity/authentication violation stemming directly from this gem's incomplete signature-binding contract.

### Likelihood Explanation
The only prerequisite is one legitimately observed webhook delivery (body + HMAC) for the shared `client_secret`, which any shop that has installed the app already receives via its own webhook endpoint without needing any secret key, access token, or privileged access — satisfying the "unprivileged internet user" bar. Forging a new HTTP request with the same body/HMAC but a different `shop-domain` header is a straightforward capture-and-replay operation with no additional cryptographic material required.

### Recommendation
Include the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used by `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop domain to the HMAC-verified payload, so that `Utils::HmacValidator.validate` cannot succeed for a body whose `shop` header has been swapped after the fact.

### Proof of Concept
1. App shares a single `client_secret` and receives real webhooks for Shop A and Shop B.
2. Attacker controls a store using the app (Shop A) and captures a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the shared secret), computed as in `lib/shopify_api/utils/hmac_validator.rb`.
3. Attacker resends the identical `B`/`H` to the app's webhook endpoint but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally (`lib/shopify_api/webhooks/request.rb:45-63`).
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only re-hashes `@raw_body` (unchanged) — the forged shop header is invisible to the check (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
6. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop == "shop-b.myshopify.com"` and delivered to the app's handler, which processes attacker-controlled body content as if it were an authentic event from Shop B.

### Citations

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
