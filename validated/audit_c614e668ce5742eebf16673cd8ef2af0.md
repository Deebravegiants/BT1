### Title
Webhook shop domain spoofing via unauthenticated header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating only the HMAC of the raw request body, but then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers when dispatching the webhook to the application handler. This breaks the identity binding `HMAC(signed_bytes) == hmac` where `signed_bytes` is expected to equal `(shop, topic, body)` but actually only equals `body`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string` (the raw body only) and compares it against `request.hmac` (parsed from the `x-shopify-hmac-sha256`/`shopify-hmac-sha256` header): [3](#0-2) [4](#0-3) 

Because `hmac_validator.validate` never includes `shop`, `topic`, or `webhook_id` in the signed content, a request whose body+HMAC pair is valid for *any* shop (the app's `api_secret_key` is shared across all installs, not per-shop) will pass validation regardless of what `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` header values are attached. The library then hands this attacker-controlled `shop` value straight to the application's webhook handler via `WebhookMetadata`: [5](#0-4) 

The identity equality the library implicitly claims to enforce is:
`hmac == HMAC_secret(shop || topic || body)`

but the actual equality enforced is only:
`hmac == HMAC_secret(body)`

with `shop`/`topic`/`webhook_id` supplied out-of-band and unauthenticated.

### Impact Explanation
Since the app's webhook secret (`api_secret_key`) is shared across every shop that installs the app, any attacker who controls a shop that has the app installed can capture a legitimately-signed `(raw_body, hmac)` pair from their own real webhook deliveries, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header for a victim shop. The gem reports this as a validly-authenticated webhook "from" the victim shop's domain. Any host application that keys tenant-scoped side effects (data writes, deletion, uninstall handling, entitlement changes) off `WebhookMetadata#shop` as returned by this gem is exposed to cross-tenant data corruption/access, since the gem's own signature check gives no actual guarantee that the claimed `shop` matches the body that was signed.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate merchant/tester with the app installed on any shop (a low-privilege, unauthenticated-from-Shopify's-perspective actor relative to other tenants) capturing one real webhook delivery, then replaying it directly to the app's public webhook HTTP endpoint with a modified header — no access to `api_secret_key`, access tokens, or victim credentials is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (whichever fields the application will trust) in the signable content used for HMAC verification, or otherwise cryptographically bind these header-derived values to the signed payload before exposing them via `WebhookMetadata`, e.g.:
```ruby
def to_signable_string
  "#{shop}|#{topic}|#{@raw_body}"
end
```
and document clearly that `shop`/`topic` are not verifiable unless explicitly bound into the signature — or perform the shop-domain existence check against Shopify's actual `X-Shopify-Shop-Domain` allowlist during webhook registration/processing.

### Proof of Concept
1. Install the app (or otherwise have webhook delivery access) on attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery `raw_body` and its `shopify-hmac-sha256` header value `hmac_valid` (valid because it's `HMAC_secret(raw_body)`, and `secret` is shared across all shops).
2. Send a new HTTP POST to the app's webhook endpoint with:
   - Body: the exact captured `raw_body`
   - Header `shopify-hmac-sha256`: `hmac_valid` (unchanged)
   - Header `shopify-shop-domain`: `victim.myshopify.com` (forged)
   - Header `shopify-topic`: unchanged or forged to a topic accepted by a registered handler
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC_secret(raw_body) == hmac_valid`, ignoring the forged `shop` header.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host application to perform shop-scoped actions attributing this data to `victim.myshopify.com` even though it did not originate from Shopify for that shop.

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
