### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable payload from the raw body only, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header. `Registry.process` accepts the request once `Utils::HmacValidator.validate(request)` passes and then hands `request.shop` straight to the handler as the tenant identity, so the byte range verified by the HMAC (`@raw_body`) does not include the byte range acted on for tenant attribution (`shop-domain` header).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop` is parsed from a separate, unsigned header: [2](#0-1) 

`Registry.process` validates the HMAC over the signable string (i.e. the body) and, once it passes, passes `request.shop` (the header value) into `WebhookMetadata` for the handler to use as tenant identity: [3](#0-2) 

Because the webhook HMAC secret (`Context.api_secret_key`) is a single per-app secret shared across every shop that installs the app — not a per-shop secret — any legitimate webhook body an attacker's own shop receives is HMAC-valid for the app in general, not bound to that specific shop. An attacker who owns a shop that has the app installed can capture a body+HMAC pair from a legitimate webhook delivered to their own store (ordinary merchant activity, no privileged access required), then resend that exact `raw_body`/`hmac-sha256` value to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` only re-derives the HMAC from `@raw_body` and compares it to the header-supplied HMAC: [4](#0-3) 

The shop header is never included in the signed bytes, so the forged request passes validation, and the app processes attacker-controlled body content as if it originated from the victim shop.

The broken identity binding, stated as an equality that should hold but does not:
`bytes_covered_by_hmac (raw_body) == bytes_used_for_tenant_attribution (shop-domain header)` — this equality is false; the header is trusted without being part of the verified payload.

This is the same bug class as the report's "value used for a security decision is not actually checked/covered by the mechanism meant to authorize it" (there, `hookParams.amAmmEnabled` bypassing the override check meant to gate the decision; here, the `shop` header bypasses the HMAC verification meant to authenticate the payload's origin/tenant).

### Impact Explanation
This enables cross-tenant confusion: a webhook payload legitimately generated for the attacker's own shop can be replayed and attributed to a different (victim) merchant's shop inside the host application, because the gem hands `request.shop` to application handlers as trusted tenant identity after HMAC validation succeeds, even though `shop` was never part of the signed data. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up the victim's stored session/data and update or act on it), this can lead to cross-tenant data corruption or disclosure — matching the "cross-tenant access" impact category (Critical).

### Likelihood Explanation
Medium: exploitation requires the attacker to operate their own shop that has the target app installed (a normal merchant, not requiring privileged access, leaked secrets, or credentials), and to capture one legitimate webhook body+HMAC pair from their own store — both of which are within reach of any unprivileged app user. The forged request is then a simple unauthenticated HTTP POST to the app's public webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the bytes verified by the HMAC, or otherwise cryptographically bind the shop domain to the payload before trusting it for tenant attribution — e.g., require the host application to independently verify that the `shop` matches a shop that is known to be entitled to the specific `webhook_id`/subscription, rather than trusting the header purely because the body's HMAC validated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers/receives a legitimate webhook for a topic they control (e.g. `orders/create`), capturing the raw POST body `B` and the `x-shopify-hmac-sha256` header `H` computed as `HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Request.new` parses `shop` as `victim.myshopify.com` from the header, while `to_signable_string` still returns `B`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)` and compares it to `H` — it matches, since neither depends on the shop header: [5](#0-4) 
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed_body_of_B, ...)`, causing the host app to process attacker-controlled `B` as if it belonged to `victim.myshopify.com`. [3](#0-2)

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
