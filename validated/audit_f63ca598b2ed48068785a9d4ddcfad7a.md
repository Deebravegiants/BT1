### Title
Webhook `shop-domain` and `topic` identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable content solely from the raw request body, while the shop identity (`x-shopify-shop-domain`), topic, API version, and webhook id are all read directly from unauthenticated HTTP headers. `Registry.process` trusts the header-derived `shop` value to dispatch data to the app's webhook handler without that value ever being covered by the signature check.

### Finding Description
`Utils::VerifiableQuery` defines an abstract contract requiring `hmac` and `to_signable_string`, and `Utils::HmacValidator.validate` verifies only that `to_signable_string` matches the HMAC using `Context.api_secret_key`: [1](#0-0) 

For OAuth callbacks, `AuthQuery#to_signable_string` binds `code`, `host`, `shop`, `state`, and `timestamp` together into the signed string, so every one of those identity-relevant fields is cryptographically bound to the signature: [2](#0-1) 

For webhooks, however, `Webhooks::Request#to_signable_string` returns only the raw body bytes: [3](#0-2) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers, which are not part of the signed payload at all: [4](#0-3) 

`Registry.process` validates the HMAC and then immediately trusts these header-derived, unauthenticated values to build the `WebhookMetadata` handed to the app's handler: [5](#0-4) 

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Because the HMAC secret (`api_secret_key`) is the same single client secret shared across every shop that installs the app, and because the signature never covers the `shop-domain`/`topic` headers, that equality does not hold. Any user who can install the app on their own store (an ordinary, unprivileged action — no special access token or leaked credential required) legitimately receives real webhook deliveries with valid `body` + HMAC pairs signed by the app's shared secret. That attacker can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a victim shop. `Utils::HmacValidator.validate` will still return `true` (it only checks the body bytes against the shared secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC check is supposed to enforce: `Registry.process`'s dispatched `shop` is not actually authenticated, only the body bytes are. Any app that uses `request.shop` from `WebhookMetadata` to look up per-merchant state, credentials, or to trigger merchant-scoped side effects (the intended and documented use of `Webhooks::Request`/`Registry`) can be manipulated into treating attacker-supplied data as if it originated from an arbitrary other shop of the attacker's choosing. This is a cross-tenant identity-binding bypass reachable by any user who can install the app once (a normal, unprivileged flow), satisfying the "Critical – cross-tenant access" bar.

### Likelihood Explanation
High. Exploitation requires no secrets beyond what a legitimate merchant already possesses: install the app on a store the attacker controls, capture one real webhook delivery (body + `x-shopify-hmac-sha256` header), then send a forged HTTP request to the app's webhook endpoint with the same body/HMAC but a different `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header. `Utils::HmacValidator.validate` performs no binding check against these headers, so the forged request passes validation deterministically every time.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed payload used by `Webhooks::Request#to_signable_string`, mirroring the approach already used in `AuthQuery`. If Shopify's own webhook HMAC only covers the body server-side (matching Shopify's documented webhook verification, which does only sign the body), then the gem must not treat the header-derived `shop` as authenticated at all — hosts consuming `WebhookMetadata#shop` need to be clearly warned, and ideally the gem should cross-check the header shop against an independently trusted source (e.g., a registered webhook's expected shop, or reject cross-shop replays via a nonce/webhook-id uniqueness check) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, completing OAuth normally (no special privilege required).
2. Attacker triggers a real webhook delivery for their shop (e.g., updates a product to fire `products/update`), capturing the raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker sends a forged POST to the app's webhook endpoint with:
   - Body `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid because it only signs the body)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic: products/update` (unchanged or forged)
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only and returns `true`, since `H` matches.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` (lines 188-199) builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and invokes the app's handler with data purportedly belonging to `victim-shop.myshopify.com`, even though the payload actually originated from `attacker-shop.myshopify.com` and was never validated against that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

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
