### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) values from raw HTTP headers, but the HMAC signature verified by `Utils::HmacValidator.validate` is computed only over the raw request body, never over these headers. `Registry.process` accepts any request whose body-HMAC matches, then hands the *unauthenticated* `shop` header straight to the app's registered handler as `WebhookMetadata#shop`. This breaks the equality the gem is supposed to guarantee: `verified_bytes == bytes_the_app_trusts_as_the_tenant_identifier`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers that are never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC solely against `verifiable_query.to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` uses that same HMAC check as the sole authenticity gate, then forwards the header-derived (unverified) `request.shop` to the developer's handler as the tenant identifier for the event: [4](#0-3) 

Because Shopify's real HMAC (computed with the app's secret over the raw body only) is identical for the same body regardless of which shop header is attached, a valid `(body, hmac)` pair captured from one legitimate webhook delivery (e.g., a webhook sent to a shop that installed the app, which an unprivileged holder of that shop can observe) can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header rewritten to any other shop's domain. `HmacValidator.validate` will still return `true` because it never inspects the shop header, so `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen shop, while the body content actually originated from a different tenant.

### Impact Explanation
This is a broken identity binding: the byte range verified by HMAC (`raw_body`) does not cover the byte range the application (via this gem's own `WebhookMetadata`) treats as the authenticated tenant (`shop`). Any app relying on the gem's contract — "if `HmacValidator.validate` passes, the returned webhook data can be trusted as authentic and attributed to `request.shop`" — can be made to process attacker-controlled data under a victim shop's identity, i.e., cross-tenant confusion/injection through the gem's own webhook-processing API. This matches the "Critical: cross-tenant access" impact bucket, since it lets one authenticated party's webhook traffic be attributed, with a passing cryptographic check, to an unrelated tenant.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and possession of one valid `(raw_body, hmac)` pair — trivially obtainable by any merchant who installs the app on their own store and observes their own webhook deliveries (no `api_secret_key`, access token, or privileged access needed). The header can then be freely modified in a replayed request because it plays no role in signature computation.

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the signable string that is HMAC-verified, or otherwise cryptographically bind them (e.g., verify `shop` against the session/shop the app expects for that webhook subscription) before exposing them via `WebhookMetadata`. At minimum, document clearly that `request.shop` is unauthenticated and must not be trusted as a tenant boundary, and provide a verified alternative.

### Proof of Concept
1. App shop A receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid, since `H = HMAC(secret, B)`), header `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
2. Attacker (who runs shop A, or intercepts the request) resends the identical `(B, H)` pair to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {... shop-domain: "shop-b.myshopify.com", hmac: H})` is constructed; `hmac` returns the decoded `H` and `to_signable_string` returns `B`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` and compares to `H` — matches, since `shop` is not part of `B`. [5](#0-4) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: parsed B, ...)` — the app now processes shop A's webhook payload as if it belongs to shop B. [6](#0-5)

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
