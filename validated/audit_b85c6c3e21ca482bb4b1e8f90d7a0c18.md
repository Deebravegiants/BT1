## Title
Webhook `shop`, `topic`, and `webhook-id` fields are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then reads the shop, topic, and webhook-id used to route and process the payload from unauthenticated HTTP headers. Because the signature never covers those header values, any party who already has one legitimately-signed `(raw_body, hmac)` pair for their own shop can replay it to the app's webhook endpoint with different `shop-domain`/`topic` headers, causing the app to process the payload under a different tenant identity than the one Shopify actually signed it for.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are all read straight from HTTP headers and are not part of the signed material: [2](#0-1) 

`Registry.process` verifies the HMAC over `to_signable_string` (the body only), and then uses the unauthenticated `request.topic` and `request.shop` header values to route to a handler and construct the `WebhookMetadata` passed into application code: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (raw body) against the secret; it never binds the shop or topic headers to the signature: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated by HMAC == shop acted upon by the handler`. In reality, only `raw_body authenticated by HMAC == raw_body` holds; `shop`/`topic`/`webhook_id` are unauthenticated bytes that the host application (via `WebhookMetadata`) is expected to treat as trustworthy tenant/topic identifiers.

Since every shop that installs the same app shares the same `api_secret_key`-derived HMAC, a merchant who has legitimately received one webhook delivery (body `B`, valid `hmac(B)`) for their own shop can resend that exact `(B, hmac(B))` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) to point at a different, victim shop. `Utils::HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will dispatch the handler using the attacker-chosen `shop` value, so the app processes shop `B`'s payload as if it belonged to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: the webhook consumer (host application, via `WebhookMetadata#shop`) has no cryptographic guarantee that the shop it acts on is the shop the payload was actually generated for. Depending on how the host app implements its `WebhookHandler`, this can be leveraged to: trigger shop-scoped side effects (e.g., data deletion/redaction handlers such as GDPR `shop/redact`, cache invalidation, uninstall cleanup) against an arbitrary victim shop, or make the app record/act on attacker-supplied data under a victim shop's identity — a cross-tenant access/data-integrity issue.

### Likelihood Explanation
Exploitation requires only that the attacker (1) operates their own shop that has the target app installed, so they legitimately receive at least one real webhook delivery, and (2) can send an HTTP request directly to the app's public webhook endpoint with forged headers — both are within reach of an unprivileged internet user/merchant, with no access to `api_secret_key` or any access token required.

### Recommendation
Include the routing-critical headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body's signature, so that `Utils::HmacValidator.validate` fails if any of these fields are altered relative to what Shopify actually signed. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated and must not be trusted for authorization decisions without additional verification (e.g., cross-checking against a known/registered shop list).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H = HMAC_SHA256(api_secret_key, B)` along with `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: shop/redact` (or any subscribed topic).
2. Attacker resends the exact same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `H` against `HMAC_SHA256(api_secret_key, B)` — unaffected by the header change.
4. The handler registered for the topic is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed B, ...)`, causing the host application to act on victim-shop's tenant context using attacker-controlled/replayed data.

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
