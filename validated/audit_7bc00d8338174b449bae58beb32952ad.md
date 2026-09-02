### Title
Webhook shop/topic attribution is not cryptographically bound to the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the request body via HMAC, then dispatches to the handler using the `shop`, `topic`, and `webhook_id` values taken straight from unauthenticated HTTP headers. Because those header fields are never included in the signed material, a party that has learned one valid `(raw_body, hmac)` pair for its own shop can resend the identical body with a different `x-shopify-shop-domain` header and the HMAC check will still pass, causing the handler to process the payload as if it originated from a different tenant.

### Finding Description
`Utils::HmacValidator.validate` computes the signature purely from `request.to_signable_string`, which for webhooks is defined as the raw body only: [1](#0-0) [2](#0-1) 

`Registry.process` uses this HMAC check as the sole authentication gate, then immediately trusts `request.topic` and `request.shop` — both parsed directly from headers that are excluded from the signed bytes — to route and label the event for the handler: [3](#0-2) [4](#0-3) 

The identity binding this breaks: `hmac_verified(bytes) == bytes_acted_on`. The gem verifies `raw_body` but acts on `shop`/`topic` headers, which are disjoint from the verified bytes. Any caller who possesses one legitimate `(body, x-shopify-hmac-sha256)` pair — e.g., an app developer/merchant who owns a store that has the app installed and can observe their own shop's webhook deliveries — can replay that exact body/HMAC combination while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header. `HmacValidator.validate` will return `true` because it only recomputes the HMAC over `raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` object asserting the forged shop as the origin of that data: [5](#0-4) 

Host applications built on this gem's documented API (registering a handler and calling `Registry.process`) have no means to detect the spoof — the library itself hands them an unauthenticated tenant identifier alongside an authenticated body, which is exactly the pattern this class of bug (checking one thing, acting on another that wasn't equivalently verified) exploits.

### Impact Explanation
This is a cross-tenant attribution bypass at the gem level: the `shop` value delivered to application webhook handlers is not bound to the cryptographic proof of authenticity. Applications typically use `data.shop` to select which merchant's records to create/update/delete (e.g., order sync, inventory updates, uninstall processing). An attacker capable of producing one authentic `(body, hmac)` pair for any shop (including their own, legitimately installed instance of the app) can cause the handler to attribute that payload to an arbitrary victim shop domain, leading to cross-tenant data corruption or unauthorized state changes scoped to another merchant — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only ordinary, unprivileged access to a webhook endpoint the attacker's own installed app instance receives (no `api_secret_key`, access token, or other elevated credential is needed) plus the ability to forge the `x-shopify-shop-domain`/`x-shopify-topic` headers on a replayed HTTP request to the app's public webhook endpoint. Because header spoofing on an HTTP POST is trivial and the same body/HMAC pair remains valid indefinitely (no nonce/timestamp binding is enforced on webhooks by this gem), likelihood is moderate-to-high for any app that trusts `WebhookMetadata#shop` for tenant-scoped operations.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` values in the HMAC-signed material (or otherwise cryptographically bind them, e.g., by having `Request#to_signable_string` incorporate the relevant headers alongside the body), so that `Registry.process` cannot dispatch a verified body under a forged tenant identity. At minimum, document and enforce that the shop derived from headers is cross-checked against an out-of-band trusted mapping (e.g., matching against the shop associated with the currently active webhook subscription/session) before invoking the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real webhook event, capturing the delivered `raw_body` and `x-shopify-hmac-sha256` header (both legitimately signed by Shopify with the app's `api_secret_key`, but observable by the receiving app owner).
2. Attacker replays an HTTP POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `shop`; `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only and returns `true` since the body/HMAC pair is authentic [6](#0-5) .
4. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [5](#0-4) , causing the application to act on the payload as belonging to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
