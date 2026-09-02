### Title
Webhook shop-tenant spoofing via HMAC that binds only the body, not the `shop`/`topic`/`webhook_id` headers used to route event data - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by checking only that the raw HTTP body matches an HMAC-SHA256 signature computed with the app's shared `api_secret_key` [1](#0-0) . The tenant-identifying fields that the handler is actually given — `shop`, `topic`, `webhook_id`, `api_version` — are read straight from HTTP headers and are **not** part of the signed material [2](#0-1) . Because the same `api_secret_key` is shared across every shop that has installed the app, an attacker who legitimately installs the app on their own store can obtain a body+HMAC pair that Shopify signs correctly for arbitrary attacker-chosen event content, then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a victim shop.

### Finding Description
`HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the received HMAC: [3](#0-2) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; the `shop`, `topic`, `webhook_id`, and `api_version` accessors read unauthenticated headers that are never mixed into the signed string: [4](#0-3) 

`Registry.process` then dispatches to the handler using these unauthenticated values directly: [5](#0-4) 

The identity binding that should hold is:
```
shop asserted in HMAC-covered bytes == shop the handler treats the event as belonging to
```
Here the equality breaks: the HMAC covers `raw_body` only, while `WebhookMetadata.shop` (and `topic`, `webhook_id`) are taken from headers outside that coverage. Any attacker who can install the app on a shop they control can generate valid `(body, hmac)` pairs for content of their choosing (by performing the corresponding action on their own store, e.g. creating an order, updating a customer, or triggering `customers/redact`/`shop/redact`), capture the delivered `raw_body` + `x-shopify-hmac-sha256`, and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only re-derives the signature from `raw_body`, and `Registry.process` passes the spoofed `shop` through to the handler unchanged.

### Impact Explanation
Depending on how the host application's webhook handler uses `WebhookMetadata#shop`, this enables cross-tenant confusion: injecting fabricated `orders/create`, `app/uninstalled`, or mandatory GDPR (`customers/redact`, `shop/redact`, `customers/data_request`) events attributed to a shop the attacker does not control. If the handler uses the spoofed shop to look up/mutate that shop's stored data (a common pattern, since this is exactly the value the library hands to the handler for that purpose), an attacker can cause cross-tenant state changes or data-deletion requests against a shop they never installed the app on.

### Likelihood Explanation
Exploitation only requires attacker-controlled infrastructure: install the app on a store the attacker owns/controls (any unprivileged internet user with a Shopify partner/dev account can do this for free), trigger any webhook topic the app subscribes to with attacker-chosen data to obtain a valid `(raw_body, hmac)` pair, then POST it to the app's public webhook endpoint with a forged shop header. No access to the app's `client_secret`, an access token, or any privileged account belonging to the victim is required.

### Recommendation
Bind the routing-critical headers into the verified material, e.g. include `shop`, `topic`, and `webhook_id` in the signed string (or verify them against a value derived independently, such as looking up the shop's own stored/expected webhook secret or session before trusting the header), rather than trusting header values that fall entirely outside the HMAC's coverage.

### Proof of Concept
1. Attacker creates a free/dev Shopify store and installs the target app, causing the app's registered webhook (e.g. `customers/redact`) to fire with attacker-chosen payload content.
2. Attacker's server captures the delivered request: `raw_body` and `X-Shopify-Hmac-Sha256` header (valid because it was genuinely signed by Shopify with the app's shared `api_secret_key`).
3. Attacker replays this exact `raw_body` + `hmac` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (it only checks `raw_body`) [6](#0-5) , and `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` [7](#0-6) , even though that shop never sent this event.

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
