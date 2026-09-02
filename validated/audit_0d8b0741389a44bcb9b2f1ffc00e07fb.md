### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop domain, topic, webhook id, and API version are read directly from unauthenticated HTTP headers and passed on to the app's handler as trusted values. Any party capable of obtaining one genuine, validly-signed webhook (e.g. by installing the public app on their own store) can replay that exact `(body, hmac)` pair while swapping the `shop-domain`/`topic` headers to any value, and `Registry.process` will accept it as authentic for the forged shop/topic.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all derived from headers that are never part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC using exactly that signable string: [3](#0-2) 

`Webhooks::Registry.process` trusts `request.topic` (to select the handler) and `request.shop` (passed straight into `WebhookMetadata` given to the app's handler) once `HmacValidator.validate` succeeds, without any additional binding check: [4](#0-3) 

The broken identity binding is:
`HMAC-verified bytes (raw_body)` ≠ `bytes acted upon (shop-domain header, topic header, webhook-id header)`.

Shopify signs app webhooks with the app's single `client_secret`/`api_secret_key`, which is identical for every shop that has installed the app. Consequently, an unprivileged internet user can:
1. Install the target public app on a store they control.
2. Receive a genuine webhook, capturing its raw body and its `shopify-hmac-sha256` value (this signature is valid because it was computed with the app's shared secret).
3. Replay this exact `(body, hmac)` pair to the app's webhook endpoint, but with an arbitrary `shopify-shop-domain` header (and/or `shopify-topic` header) pointing at a different, victim shop.

Because `to_signable_string` never includes the shop or topic, `HmacValidator.validate` still returns `true`, and `Registry.process` dispatches to the handler with `data.shop` set to the attacker-chosen victim shop domain and/or `data.topic` set to an attacker-chosen topic, while `data.body` is the attacker's own (but genuinely signed) payload.

### Impact Explanation
This directly breaks the tenant-isolation guarantee the gem is supposed to provide via HMAC verification of webhooks: host applications rely on `WebhookMetadata#shop` (and `#topic`) as an authenticated statement of which shop generated the event. Since these fields are unauthenticated, a single attacker who can trigger any webhook for their own store (installing a public app is enough) can make the library report that event as belonging to any other tenant's shop, or under any topic the attacker chooses whose handler is registered. Depending on how the host app uses `data.shop` (e.g. to look up/update per-shop records, trigger uninstall/GDPR-type flows, or drive billing/topic-specific logic), this yields cross-tenant data corruption or state confusion — meeting the "cross-tenant access" criterion for Critical/High impact.

### Likelihood Explanation
Likelihood is high for any app that is publicly installable (the normal Shopify app model): no privileged credentials, access tokens, or `api_secret_key` knowledge are required by the attacker — only the ability to install the app on a store they control and capture one legitimate webhook delivery, then replay it with modified headers to the app's public webhook endpoint.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload validated by `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind them to the signed body (e.g. verify against Shopify's documented signing scheme that covers these headers, or require the host app to independently confirm `shop` against a known/expected value before trusting the payload). At minimum, document clearly that `data.shop`/`data.topic` are NOT covered by the HMAC and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook subscription (e.g. `orders/create`) and captures the raw POST body `B` and header `shopify-hmac-sha256: H`, which validates because `H = HMAC_SHA256(api_secret_key, B)`.
3. Attacker resends a request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `shopify-hmac-sha256: H` (unchanged, still valid since only `B` is signed)
   - `shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `shopify-topic: orders/create` (unchanged or changed to another registered topic)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` returns `B` and the HMAC over `B` is still valid: [5](#0-4) 
5. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop = "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop: [6](#0-5)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
