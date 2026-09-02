Found it: `Webhooks::Request` binds only the raw body to the HMAC, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with zero cryptographic binding to that signature.

### Title
Webhook shop/topic/metadata spoofing via header–body binding gap - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values that the handler receives are pulled from unauthenticated HTTP headers and are never included in the signable string, so they are never covered by the HMAC that is verified.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , and `Utils::HmacValidator.validate` computes the HMAC over exactly that signable string and compares it against the `hmac` value taken from the `x-shopify-hmac-sha256`/`shopify-hmac-sha256` header [3](#0-2) . Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are read directly from request headers with no signature coverage at all [4](#0-3) .

`Registry.process` uses these unauthenticated header values to select the handler and to populate `WebhookMetadata` passed to application code: `handler = @registry[request.topic]&.handler` and `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [5](#0-4) .

The binding that is broken, stated as an equality that should hold but does not:
`bytes_verified_by_hmac == bytes_the_handler_acts_on`

Before the request: `bytes_verified_by_hmac = raw_body` (only). `bytes_the_handler_acts_on = {shop, topic, webhook_id, api_version, raw_body}`.
After a successful HMAC check: the equality still fails for `shop`, `topic`, `webhook_id`, `api_version` — none of these are constrained by the valid signature. An attacker who can produce *any* valid `(body, hmac)` pair for the app's secret (e.g., by triggering one legitimate webhook delivery for a topic/body they control, such as a topic the app subscribes to for their own trial/dev shop) can replay that exact `body` + `hmac` pair to the app's webhook endpoint while forging the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers to arbitrary values. `HmacValidator.validate` will still pass because it only checks the raw body against the HMAC, and the forged `shop`/`topic` will be delivered to the app's handler as if genuinely originating from that shop/topic.

### Impact Explanation
This crosses the "shop authenticated versus shop stored as identity" boundary described in the report analogy: the handler is told an unauthenticated `shop` value is the origin of an HMAC-legitimate payload. Depending on how the host application uses `WebhookMetadata#shop` and `#topic` (e.g., looking up per-shop tenant data, dispatching mandatory GDPR webhooks like `shop/redact`/`customers/redact`, or writing merchant-scoped records), this enables cross-tenant data confusion: an attacker who owns one shop and can capture one valid `(body, hmac)` pair for a subscribed topic can cause the app to process that payload under a different, victim shop's identity, or under a spoofed topic that triggers different unauthenticated code paths in the handler. This matches the Critical bucket "cross-tenant access" since it defeats the identity guarantee (`shop`) that this gem is expected to provide alongside HMAC verification.

### Likelihood Explanation
Requires the attacker to have received at least one legitimately-signed webhook body from Shopify for the same `client_secret`-scoped app (trivial for any merchant who has the app installed on their own store, since HMAC is computed only over the body, not tied to a specific shop or timestamp), and to be able to reach the app's public webhook endpoint with arbitrary headers (standard for any internet-reachable webhook receiver). No access token, `api_secret_key`, or privileged account is needed — only interaction with the app as an ordinary merchant/webhook sender.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop` and `topic`) in the HMAC-signable string in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind these header-derived fields to the verified payload before constructing `WebhookMetadata`, so a valid signature can only be replayed for the exact shop/topic it was issued for.

### Proof of Concept
1. App has the gem installed and subscribes to at least one webhook topic (e.g., `orders/create`).
2. Attacker installs the app on their own shop `attacker-shop.myshopify.com` and triggers that topic, capturing a legitimate `(raw_body, x-shopify-hmac-sha256)` pair delivered by Shopify (this pair is valid because `HmacValidator` only checks `raw_body` against the app's secret, per `lib/shopify_api/utils/hmac_validator.rb`).
3. Attacker replays an HTTP POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-topic` value.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body` (`to_signable_string`) [2](#0-1) .
5. `Registry.process` looks up the handler by the forged `request.topic` and invokes it with `shop: request.shop` set to the forged victim shop domain [5](#0-4) , causing the application-level webhook handler to act on attacker-supplied body content under the victim shop's/spoofed topic's identity.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L192-199)
```ruby
          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
