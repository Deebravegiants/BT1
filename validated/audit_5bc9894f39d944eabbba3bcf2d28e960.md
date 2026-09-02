### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw HTTP body only, while the `shop`, `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are read directly from unauthenticated headers. Anyone who can obtain one legitimately-signed `(body, hmac)` pair for the app's shared `api_secret_key` — e.g. a merchant that has installed the app on their own store and observes their own webhook deliveries — can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and/or `shopify-topic`) header. `HmacValidator.validate` will accept the request because it only checks the body's signature, and the handler will then execute business logic believing the webhook came from a different shop/topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, and `#webhook_id` are pulled straight from HTTP headers that are not part of that signed string: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e. the raw body) and then immediately trusts `request.shop` / `request.topic` to dispatch to the registered handler and to build `WebhookMetadata`: [3](#0-2) 

`HmacValidator.validate` in turn only recomputes/compares the signature over `verifiable_query.to_signable_string`, which for a webhook request is just the body: [4](#0-3) 

This breaks the intended identity binding: `HMAC(body) == HMAC(body)` is satisfied, but the equality that actually matters for tenant isolation — `shop header == shop the body was originally signed for` — is never checked. Because the app's `api_secret_key` is shared across every shop/tenant using the app, a valid `(body, hmac)` pair generated for one shop's webhook remains cryptographically valid when replayed with a forged `shopify-shop-domain` (or `shopify-topic`) header for a different shop/topic.

### Impact Explanation
This allows cross-tenant impersonation: an attacker who is a legitimate (even free/trial) merchant of the app can capture a webhook delivery to their own endpoint (e.g. an `orders/create` or `app/uninstalled` payload with body `B` and valid `hmac(B)`), then POST that same `(B, hmac(B))` to the app's webhook endpoint again with a different `shopify-shop-domain` header. The library reports the HMAC as valid and hands the handler a `WebhookMetadata` claiming the payload belongs to an arbitrary shop of the attacker's choosing, and/or an arbitrary topic. Depending on what the host app's webhook handler does with `shop`/`topic` (e.g. deprovisioning that shop, marking it uninstalled, crediting an order, updating tenant-scoped state), this can result in cross-tenant data manipulation or unauthorized state changes attributed to a shop the attacker does not control — satisfying the "cross-tenant access" impact class.

### Likelihood Explanation
Reachable by any unprivileged internet user with access to (a) a public webhook endpoint of an app built on this gem, and (b) one legitimately-signed payload from that app (trivially obtainable by installing the free/trial version of the target app on the attacker's own development store, which is the normal way third-party apps are distributed on Shopify). No access to `api_secret_key`, access tokens, or privileged accounts is required — only replay of a header that was never bound into the HMAC.

### Recommendation
Include the identity-relevant fields (`shop-domain`, `topic`, and ideally `webhook-id`) in the HMAC-signed content, or otherwise cryptographically bind them, so that a signature computed for one shop/topic cannot be replayed for another. At minimum, `Request#to_signable_string` should incorporate the shop domain and topic headers (consistent with how `AuthQuery#to_signable_string` binds `shop`, `host`, `code`, `state`, and `timestamp` together) so `HmacValidator.validate` actually authenticates the tenant/topic attribution, not just the raw body bytes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker-shop.myshopify.com`) and triggers a webhook, e.g. `orders/create`, capturing:
   - `raw_body = B`
   - `hmac = Base64(HMAC-SHA256(api_secret_key, B))`
   - headers: `shopify-topic: orders/create`, `shopify-shop-domain: attacker-shop.myshopify.com`
2. Attacker replays the exact same `raw_body` and `hmac` to the app's public webhook endpoint, but changes the header:
   - `shopify-shop-domain: victim-shop.myshopify.com`
   - (optionally) `shopify-topic: app/uninstalled`
3. In the gem:
   ```ruby
   request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {
     "shopify-topic" => "app/uninstalled",          # forged
     "shopify-hmac-sha256" => captured_hmac,        # still valid, body unchanged
     "shopify-shop-domain" => "victim-shop.myshopify.com" # forged
   })
   ShopifyAPI::Webhooks::Registry.process(request)
   ```
4. `Utils::HmacValidator.validate(request)` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:12-31`) because it only checks `B` against `captured_hmac`, both untouched.
5. The registered handler for `app/uninstalled` is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though the payload/signature was never produced for that shop.

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
