### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unsigned `shop-domain` header as the tenant identity that gets handed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an HTTP header and is never part of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` and compares it to the received `hmac`, without incorporating `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` only checks this body HMAC, then immediately trusts `request.shop` as the tenant identity that is forwarded to the app's webhook handler: [4](#0-3) 

The broken identity binding, expressed as an equality that the gem fails to enforce:
`HMAC-verified bytes (raw_body)` ≠ `identity bytes acted upon (shop header)`.

Because the app's webhook secret (`Context.api_secret_key`) is shared across every merchant that has installed the app (it is not per-shop), any legitimate merchant already possesses valid `(raw_body, hmac)` pairs signed with that same shared secret from their own genuine webhook deliveries. Since the `shop-domain` header is excluded from the signed content, that merchant can replay the exact same signed body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` because the signature check never looks at that header, and `Registry.process` passes the attacker-chosen `shop` value straight into `WebhookMetadata`, which the host app uses to attribute the event to a tenant.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to provide: an unprivileged user who only controls their own store (and thus only needs the ability to trigger any webhook-eligible event on their own shop, or intercept traffic to their own installation) can forge webhook events that the app will process as belonging to a different, victim shop. Depending on what the app's webhook handlers do with `WebhookMetadata#shop` (e.g. updating billing state, order records, or GDPR/compliance actions keyed by shop), this enables cross-tenant data corruption/access — the impact class explicitly called out as Critical in the rules ("cross-tenant access").

### Likelihood Explanation
Likelihood is realistic but not trivial: it requires the attacker to (a) be a legitimate merchant/user of the app on some shop, (b) capture at least one raw `(body, hmac)` pair from a genuine webhook delivered to the app (achievable since they control their own store's traffic patterns and can proxy/log requests to their own endpoint, or via a shared/self-hosted app instance), and (c) know or guess a victim shop domain (which is public — `*.myshopify.com`). No knowledge of `api_secret_key` is required, since the attacker reuses a signature Shopify itself already generated for them.

### Recommendation
Bind the tenant-identifying header into the HMAC verification so that a signature is only valid for the exact `(shop, topic, webhook_id, body)` tuple it was generated for, or otherwise cryptographically bind `shop` before it is handed to consumers — e.g., extend `Request#to_signable_string` (or add a secondary check in `Registry.process`) to incorporate `shop`, `topic`, and `webhook_id` into what is verified, so that changing any of these headers invalidates the signature.

### Proof of Concept
1. Attacker installs the app on their own shop (`attacker-shop.myshopify.com`) and triggers any subscribed webhook topic (e.g. `orders/create`).
2. Attacker captures the raw POST body and the `x-shopify-hmac-sha256` value Shopify sent to the app's webhook endpoint for that event (e.g., via a logging proxy in front of their own receiving endpoint).
3. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` (from the unmodified header) still matches `Digest.hexencode(...)` of the unmodified body.
5. `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only and returns `true`.
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the host app to process an attacker-controlled event as though it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
