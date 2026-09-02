### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is taken from unauthenticated headers not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the tenant-identifying `shop` field (and `topic`, `webhook_id`, `api_version`) come from HTTP headers that are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` when building the `WebhookMetadata` passed to the app's handler, so the "shop the HMAC proves came from Shopify" and "the shop the handler acts on" are two different, independently-controllable values.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from the (unsigned) HTTP headers via `shopify_header`: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC over the request (i.e. the body) and, once it passes, builds `WebhookMetadata` using `request.shop`/`request.topic`/`request.webhook_id` taken from those same unsigned headers: [4](#0-3) 

`HmacValidator.validate` / `validate_signature` compute the signature only from `verifiable_query.to_signable_string` (the body) against `Context.api_secret_key`: [5](#0-4) 

The binding that should hold is:
`shop authenticated by HMAC == shop the handler is told the event came from`

Because the signature only covers `@raw_body`, this equality is never enforced. `Context.api_secret_key` is the same `client_secret` for the app across *every* merchant that installs it. An attacker who controls or installs the app on their own store (or otherwise legitimately triggers one webhook delivery under their own shop) has a body+HMAC pair that is valid under the app's secret. Because the header set (`shop-domain`, `topic`, `webhook-id`, `api-version`) is completely unauthenticated, that attacker can resend that identical `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with an arbitrary victim shop domain and topic. `Utils::HmacValidator.validate` still passes because it only checks the (unchanged) body against the secret, and `Registry.process` then hands the host application a `WebhookMetadata` claiming the event is for the victim shop/topic/webhook id even though it never originated from Shopify for that shop or topic.

### Impact Explanation
Any host application built on this gem's documented webhook-processing API (`ShopifyAPI::Webhooks::Registry.process`) receives `WebhookMetadata#shop` as an already-"verified" value once `Errors::InvalidWebhookError` is not raised. If that application uses `data.shop` to look up/update per-tenant state (as the gem's own docs and tests demonstrate, e.g. `data.shop` used to dispatch tenant-specific side effects), an attacker can cause cross-tenant confusion: injecting attacker-controlled body content that is HMAC-valid (from their own shop) but attributed to a victim shop/topic, or replaying the same payload against many different `shop-domain` values. This is a cross-tenant identity-binding break carried entirely by the gem's own webhook verification contract, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
This requires no privileged access: an unprivileged internet user only needs to be able to install the target app on any shop they control (a normal signup flow) to obtain one legitimate `(raw_body, hmac)` pair for an event type of their choosing, then replay it against the app's public webhook endpoint with modified `shop-domain`/`topic`/`webhook-id` headers. No knowledge of `Context.api_secret_key` is needed since the attacker never has to compute a new HMAC — they reuse a valid one.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used by `Request#to_signable_string`, or otherwise cryptographically bind them to the HMAC, so `HmacValidator.validate` fails if any of these fields are altered relative to what Shopify actually signed. At minimum, document/require callers to independently verify `shop` against a known/installed-shop allowlist before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Install the vulnerable app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) to capture a valid `raw_body` and `x-shopify-hmac-sha256` header signed with the app's `client_secret`.
2. Send a POST to the app's webhook endpoint with the same `raw_body` and `hmac-sha256` header, but set:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: orders/create` (or a different registered topic)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the secret and passes.
4. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)`, i.e., the host application processes attacker-controlled event data as if it were an authentic event for the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
