### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Utils::HmacValidator` verify the authenticity of a webhook by computing an HMAC over the raw request body only. The `shop` (and `topic`, `webhook_id`, `api_version`) values are parsed independently from unauthenticated HTTP headers and are never included in the signed bytes. Any party who can obtain one validly-signed body/HMAC pair (trivially available to any unprivileged internet user by installing the app on their own store) can replay that exact body/HMAC to the app's webhook endpoint while swapping the `shop` header to a victim shop domain, and the signature check still passes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic tie to the HMAC: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it only checks the body bytes against the secret — it never checks that `shop` (or `topic`/`webhook_id`) is bound to that signature: [3](#0-2) 

`Registry.process` performs exactly this check-then-trust sequence: it validates the HMAC of the body, then builds `WebhookMetadata` using the unauthenticated `request.shop` header and hands it to the app's handler: [4](#0-3) 

The identity binding that the gem implicitly promises to the host application is:

`HMAC_valid(body, secret) == true` implies `shop_header == shop_that_produced_this_body`

In reality the equality that holds is only `HMAC(secret, raw_body) == received_hmac`; the `shop` header is independently parsed and carries no cryptographic relationship to that signature. `bytes verified` (the raw body) ≠ `bytes parsed` (the shop header used for tenant attribution), which is exactly the class of binding failure this gem must avoid for its own webhook-verification API.

### Impact Explanation
Any unprivileged internet user can self-install the app on their own Shopify development/trial store (no privileged credential of the victim is required) and thereby legitimately receive a validly-signed webhook body/HMAC pair for their own tenant. Because the `shop` header is outside the signed bytes, that same body+HMAC can be replayed directly against the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to an arbitrary victim shop. `Registry.process` will accept it (HMAC still valid) and dispatch attacker-controlled body content to the app's handler tagged as belonging to the victim shop (`WebhookMetadata#shop`). Any host application that uses `data.shop` for tenant attribution — the exact purpose `WebhookMetadata` exists for — will store, create, or act on data under the wrong tenant's identity. This is a cross-tenant integrity/confusion vector reachable by any unauthenticated network attacker, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. No credentials, access tokens, or `client_secret` are needed. Obtaining a legitimately-signed body is as simple as installing the app on a free/self-owned store (a normal, unprivileged flow), and forging the header swap is a single HTTP request with attacker-controlled headers. The only prerequisite is that the app exposes a webhook endpoint that calls `Registry.process`, which is the gem's documented, intended usage pattern.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed payload used by `to_signable_string`, or otherwise cryptographically bind the `shop` header to the verified body (e.g., verify shop ownership out-of-band via session lookup, or require the HMAC to cover a canonicalized representation of headers + body) before constructing `WebhookMetadata` in `Registry.process`. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a real webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid signature of `B`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker sends a POST directly to the app's public webhook endpoint with the same raw body `B` and the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `HMAC(secret, B)` — this still passes: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, so the host app processes attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

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
