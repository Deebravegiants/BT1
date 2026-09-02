### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook only by validating the HMAC over the raw request body, then dispatches the event to the app's handler using a `shop` value read directly from an HTTP header that is never included in that HMAC computation. This breaks the equality that the caller implicitly relies on: `HMAC-verified bytes == tenant-identifying bytes`. Any request carrying a validly-signed body can be relabeled to any shop by simply changing the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header, since the header is not part of the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from an unauthenticated header: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over `to_signable_string` (i.e., the raw body), using the app's `api_secret_key`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof of the entire request's authenticity, then immediately forwards the unauthenticated `request.shop` to the app's handler as the tenant identifier for the event: [4](#0-3) 

Because Shopify signs a webhook body with the app's single `api_secret_key` (the same secret for every shop that installs the app), the signature is shop-agnostic. Anyone who can obtain one validly-signed `(body, hmac)` pair for the app — e.g., a merchant of Shop A triggering a webhook for their own store — can resend that exact `(body, hmac)` pair to the app's webhook endpoint while swapping the `shop-domain` header to Shop B. `HmacValidator.validate` still passes (it never looks at the shop header), and `WebhookMetadata.shop` is populated with the attacker-chosen value, so the handler processes/attributes the event under an arbitrary victim tenant.

This is the exact analog called out in the rules: a field acted on (`request.shop`, used for tenant attribution/session lookup by host apps) that is not covered by the HMAC that is otherwise treated as the sole authenticity proof.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), which the rules classify as Critical. Any app handler that uses `WebhookMetadata#shop` to look up or mutate shop-scoped state (session storage, per-shop settings, order/inventory records, webhook-driven billing state, etc. — exactly the pattern shown in the gem's own docs and tests) can be made to act on/for the wrong merchant using data an attacker fully controls, without ever possessing the app's `api_secret_key` or the victim's access token.

### Likelihood Explanation
Obtaining one valid `(body, hmac)` pair only requires being a legitimate (even free/trial) installer of the target app and triggering any webhook topic on your own store — no privileged access or secret is required. Replaying it with a modified `shop-domain` header is a simple HTTP request rewrite. The library provides no header-shop binding to prevent this, so exploitability depends entirely on host-app logic trusting `WebhookMetadata#shop`, which is the documented and tested way to use this field.

### Recommendation
Include the shop domain (and topic) in the signed payload verification path, or otherwise cryptographically bind the shop identity to the HMAC-covered content — for example, require `Registry.process` to validate that the `shop` header matches a shop for which the caller has an active, independently-authenticated session, or extend `to_signable_string` in `Webhooks::Request` to incorporate the relevant Shopify-provided headers used for tenant attribution before computing/validating the digest.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g., `orders/create`) on their own store, capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sends — `H` is valid because `HMAC(api_secret_key, B) == H`.
2. Attacker sends a new POST to the app's webhook endpoint with the identical body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the request; `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` and finds it equals `H` (per [5](#0-4) ), so validation passes.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...))` (per [6](#0-5) ), causing the app to process attacker-controlled data under the victim shop's identity.

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
