This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop` is read from the `shop-domain` header outside the signed content, and `Registry.process` passes that unauthenticated `shop` straight into `WebhookMetadata` for the host app's handler.

### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using `Utils::HmacValidator`, but the HMAC signature covers only the raw request body, not the `shop-domain` header. Since a single app's `client_secret`/`api_secret_key` is shared across every merchant that installs the app, any holder of one valid, correctly-signed webhook (i.e., any merchant who has the app installed) can replay that exact body with a different `shop-domain` header and still pass HMAC validation, causing the payload to be attributed to an arbitrary victim shop.

### Finding Description
The equality that should hold is: `shop_the_HMAC_authenticates == shop_the_handler_acts_on`. In this gem it does not.

- `Request#to_signable_string` signs only the body: [1](#0-0) 
- `Request#shop` is read from a header that is completely outside that signed string: [2](#0-1) 
- `HmacValidator.validate` computes and compares the signature strictly against `to_signable_string`, i.e., the body only: [3](#0-2) 
- `Registry.process` accepts the request once the body-only HMAC checks out, then forwards the unauthenticated `request.shop` value straight to the app's handler as if it were verified: [4](#0-3) 

Because `api_secret_key`/`client_secret` is a per-app secret (not per-shop), every shop that installs the app can compute a valid HMAC for its own webhook traffic. An attacker who is themselves a legitimately installed merchant (or who otherwise captures one valid webhook `raw_body`+HMAC pair) can resend the identical body with the `shop-domain` (or `x-shopify-shop-domain`) header changed to a victim shop's domain. `HmacValidator.validate` will still return `true` because it only recomputes the signature over `@raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop, even though the shop identity was never bound to the signature.

### Impact Explanation
Any downstream code that trusts `WebhookMetadata#shop` (or `Request#shop`) to select which tenant's session/access token to load, which merchant record to mutate, or which store's data to overwrite, can be tricked into acting on behalf of a shop the attacker does not control — this is a cross-tenant access vector directly attributable to a field ("shop") that is acted upon but excluded from the cryptographic binding, matching the impact category of cross-tenant access.

### Likelihood Explanation
Exploitation requires only that the attacker be able to trigger at least one legitimate webhook delivery for some shop where the app is installed (trivial for a self-service Shopify app, since anyone can install a public app on their own store) and the ability to POST an HTTP request with modified headers to the app's own webhook endpoint (no special network position, TLS interception, or leaked secret required). No `api_secret_key`, access token, or privileged account is needed to mount the spoof.

### Recommendation
Bind the shop identity into the signed content, or otherwise independently verify it: e.g., require the app to compare `request.shop` against the shop stored for the session/webhook subscription that Shopify's GraphQL registration returned, or extend `to_signable_string` / `HmacValidator` usage so that the validated set of bytes includes the `shop-domain` header alongside the raw body before it is trusted as the tenant identifier in `WebhookMetadata`.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; capture one legitimate webhook POST — raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Replay the exact same body `B` and HMAC header `H` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)` (via [1](#0-0)  and [3](#0-2) ) which matches `H`, so validation passes.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` — see [5](#0-4)  — even though the signature never authenticated that shop value, letting the attacker-controlled body be processed under the victim's identity.

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
