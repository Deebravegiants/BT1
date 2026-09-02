## Title
Webhook HMAC only signs the raw body, not the `shop-domain`/`topic` headers, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` so that `Registry.process` can validate the webhook's authenticity via HMAC before dispatching it to the app's handler. However, the signable string used for HMAC verification is derived **only from the raw request body**, while the `shop` and `topic` values that are trusted and acted upon by `Registry.process` come from unauthenticated HTTP headers that are never included in the HMAC computation.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`HmacValidator.validate` computes the expected signature purely from `to_signable_string`, i.e. the body, and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` trusts `request.shop` and `request.topic` for dispatch as soon as the HMAC check passes, without any additional verification that these header values are the ones the signature was actually computed for: [4](#0-3) 

**Identity binding broken (as an equality):**
`hmac_valid_for(body)` is treated as if it implies `hmac_valid_for(shop, topic, body)`, but the equality
`signed_bytes == acted_on_bytes` does not hold — `signed_bytes = raw_body` while `acted_on_bytes = {shop, topic, webhook_id, api_version, raw_body}`.

**Before/after the attacker's request sequence:**
- Before: A legitimate webhook for `victim-shop.myshopify.com` (or any shop under the attacker's control, e.g. their own test/dev shop where they can observe outgoing webhooks) is delivered with body `B`, and a valid `hmac = HMAC(secret, B)`.
- Attacker action: Replay the exact same `body=B` and `hmac` value, but substitute the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header with a different, victim tenant's shop domain that is also installed on the same multi-tenant app.
- After: `HmacValidator.validate` still succeeds (only `B` and `hmac` are checked), and `Registry.process` dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: ..., ...)` with the attacker-chosen `shop` value, causing the host application's webhook handler to act on tenant data/session keyed to a shop the attacker does not control.

### Impact Explanation
This breaks the tenant/shop identity binding an app relies on when it looks up the corresponding `Session`/shop record using `WebhookMetadata#shop` after HMAC validation "proves" authenticity. Since shop-domain is not covered by the signature, an attacker who can capture one valid `(body, hmac)` pair (e.g., from their own installed instance of the app, which they legitimately receive) can relabel it to any other shop and have the app process it as if it came from that other tenant — a cross-tenant access/data-integrity issue. This matches the "Critical — cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to possess one legitimately-delivered webhook `(body, hmac)` pair (trivially available to any merchant/developer who installs the app themselves) and the ability to send a crafted HTTP request with substituted headers to the app's webhook endpoint — both are achievable by an unprivileged internet user with no access token, `client_secret`, or other privileged credential. The likelihood depends on the specific webhook topic/body being replayable in a way that's meaningful to the target shop (e.g., `app/uninstalled`, or any topic whose body doesn't itself encode the shop), which is common since most Shopify webhook payloads reference internal Shopify resource IDs rather than the shop domain itself.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the signable content used for verification, or otherwise cryptographically bind them to the request before trusting `request.shop`/`request.topic` in `Registry.process`. At minimum, document that host applications must independently verify that the shop domain in the webhook headers corresponds to an actual installed/authorized shop before acting on webhook data, since the HMAC alone does not guarantee header integrity.

### Proof of Concept
1. App receives a legitimate webhook with `raw_body = B` and header `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the identical `raw_body = B` and identical `hmac` header, but sets `x-shopify-shop-domain = victim-shop.myshopify.com` and, if desired, a different `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches the forged request's hmac header — validation **succeeds**.
4. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: forged_topic, body: parsed_body, ...))`, causing the host app to process attacker-controlled data under the victim shop's identity.

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
