### Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` headers are trusted by the webhook processor without being covered by the HMAC signature, allowing cross-tenant shop-attribution spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values, however, are all read from HTTP headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) that are never part of that signed content [3](#0-2) . `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then immediately hands the unauthenticated header-derived `shop`, `topic`, and `webhook_id` values to the host app's handler via `WebhookMetadata` [4](#0-3) . This breaks the identity binding `authenticated_body == attributed_shop`: the body's authenticity is proven, but the shop it is attributed to is not.

### Finding Description
The intended security property is that once `Utils::HmacValidator.validate(request)` returns `true`, every field the host application acts on (in particular the shop identity used for tenant-scoped side effects) should be provably tied to that Shopify-issued signature. Instead, the HMAC only binds the raw JSON body; the tenant-identifying `shop-domain` header, along with `topic`, `webhook-id`, and `api-version`, are read straight from unauthenticated headers and passed to `handler.handle` unmodified [5](#0-4) .

Because a webhook delivery endpoint is a plain public HTTP(S) endpoint, any unprivileged internet user who can obtain one legitimately-signed `(raw_body, hmac)` pair — for example, a merchant installing the app on their own shop and triggering a webhook event they control (order/product create, etc.) — can capture that request off the wire and replay it to the app's webhook endpoint with an altered `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header while leaving the body untouched. `HmacValidator.validate` will still succeed because it only checks the (unchanged) body against the (unchanged) HMAC [6](#0-5) , yet `Registry.process` will dispatch the handler with the attacker-chosen `shop` value [5](#0-4) .

This exactly matches the report's bug class of a "field acted on but not covered by the HMAC": the consensus-vs-execution mismatch in the report corresponds here to the HMAC-signed-body-vs-header-derived-shop mismatch — data that determines behavior (`shop`) is disjoint from the data the cryptographic check actually covers (`raw_body`).

### Impact Explanation
Host applications built on this gem are expected to key all per-tenant persistence, access-control, and business logic off `WebhookMetadata#shop` (the documented purpose of webhook processing is exactly this: identifying which merchant/shop an event belongs to). An attacker who forges the `shop` attribution on an otherwise validly-signed webhook can cause the host app to apply another merchant's legitimate webhook payload (e.g., an order-paid, app/uninstalled, or GDPR data-request event) under a victim shop's identity, resulting in cross-tenant data confusion or unauthorized tenant-scoped side effects (e.g., triggering uninstall/cleanup logic, GDPR erasure, or state changes) against a shop the attacker does not control. This is a cross-tenant integrity/identity-confusion issue.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the target app on any shop they control (or otherwise legitimately triggers one webhook delivery), (2) they capture the raw POST request (body + headers) sent to the app's public webhook endpoint, and (3) they resend it to the same public endpoint with a modified `shop-domain` (and/or `topic`/`webhook-id`) header. No secrets, TLS interception, or privileged access are required — the webhook endpoint is a normal public HTTP endpoint and the gem performs no header-to-body binding.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the HMAC-covered signable string (or otherwise cryptographically bind them, e.g. concatenate them with the body before hashing, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes all security-relevant fields rather than just one) so that any tampering with these header values invalidates the signature in `Utils::HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/paid`).
2. Shopify delivers a POST to the app's webhook endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/paid`, `x-shopify-hmac-sha256: <valid HMAC of body>`
   - Body: `{"id": 1, ...}` (attacker-controlled order content, since it's the attacker's own shop)
3. Attacker captures this exact request and resends it directly to the app's public webhook URL, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unmodified body) and succeeds [7](#0-6) .
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` [8](#0-7)  and the host app processes the attacker's payload as if it belonged to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
