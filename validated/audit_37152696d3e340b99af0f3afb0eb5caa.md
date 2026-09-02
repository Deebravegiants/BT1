### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification in `HmacValidator.validate` authenticates the body bytes but never binds the `x-shopify-shop-domain` header. `Registry.process` passes that unauthenticated header straight into `WebhookMetadata#shop`, which host applications use as the tenant identifier for the incoming webhook. An unprivileged user who can get any one genuine (body, HMAC) pair from Shopify — trivially available by installing the app on their own store — can replay that exact body/HMAC pair while swapping the shop-domain header to a victim shop, and the signature check still passes.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

Only `@raw_body` is signed. The `shop` accessor, however, is read straight from the header with no cryptographic binding to the signed bytes: [2](#0-1) 

`Registry.process` verifies the HMAC over the body only, then forwards the unauthenticated `request.shop` to the application handler as the tenant identity for the event: [3](#0-2) 

The identity binding that should hold is: `shop_bound_by_signature == shop_used_by_handler`. Here the left side doesn't exist at all — the signature binds nothing but the body — while the right side is attacker-controlled header data. Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-shop secret), any merchant who installs the app receives real webhooks with valid `(body, hmac)` pairs signed under that same app secret. That merchant can then replay the identical body and HMAC to the app's webhook endpoint while changing only `x-shopify-shop-domain` to a victim shop's domain. `HmacValidator.validate` recomputes the HMAC of the (unchanged) raw body and it matches, so the forged request is accepted and handed to the registered handler tagged with the victim's shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook events: an attacker who legitimately installed the app (an unprivileged, self-service action) can make the app process attacker-chosen webhook payloads (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`, or any subscribed topic) under the identity of an arbitrary victim shop. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., looking up/deleting the victim's stored session, purging the victim's data, or triggering GDPR-style redaction flows for the victim), this can cause cross-tenant data manipulation or denial of the victim's app functionality — matching the "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is moderate to high: it requires no secret, credential leakage, or privileged account — only that the attacker can install the target Shopify app themselves (open to any internet user for public apps) to obtain one legitimate `(body, hmac)` pair, and can send an HTTP POST with a forged `x-shopify-shop-domain` header to the app's public webhook endpoint. No other validation in `Registry.process` cross-checks the header shop against any authenticated value.

### Recommendation
Include the shop-identifying header (and other identity-relevant headers such as topic/webhook-id) in the signable payload the HMAC protects, or otherwise cryptographically bind `request.shop` to the verified body (e.g., require the host app to independently confirm the shop domain against a known, previously-authenticated session/store before acting on webhook data). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted as a tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, receiving a legitimate webhook, e.g. for `app/uninstalled`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker resends the same raw body `B` and the same `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `to_signable_string` returns `B` unchanged.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)` and it equals `H`, so validation succeeds: [4](#0-3) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the host app to act as though the event originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
