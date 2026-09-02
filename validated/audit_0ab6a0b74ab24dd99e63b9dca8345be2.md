### Title
Webhook shop/topic identity spoofing – HMAC covers only the raw body, not the `shop-domain`/`topic` headers - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes the signable HMAC content from `@raw_body` only, while the tenant-identifying `shop` and dispatch-controlling `topic` values are read from separate, unauthenticated HTTP headers. `Webhooks::Registry.process` trusts `request.shop` and `request.topic` for routing/tenant attribution as soon as `HmacValidator.validate` passes, but that validation never covers those two fields.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are pulled straight from HTTP headers with no cryptographic binding to the body/HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` (used identically for OAuth queries and webhook requests via the shared `VerifiableQuery` interface) verifies `verifiable_query.to_signable_string` against the app's `api_secret_key`: [3](#0-2) [4](#0-3) 

Since `to_signable_string` only returns the body, the HMAC proves "this body was signed with the app's `client_secret`" — it says nothing about which shop or topic the signer intended. `Registry.process` then uses the unauthenticated `shop`/`topic` headers directly to route and tag the webhook payload for the app's handler: [5](#0-4) 

The identity binding that should hold is: `HMAC-verified(body) == HMAC-verified(shop, topic, body)`. In this gem it only holds for `body`; `shop` and `topic` are asserted, not verified. Because Shopify signs *all* webhooks for an app with the same app-level `client_secret` (not a per-shop secret), any merchant who has installed the app can legitimately receive a genuine `(raw_body, hmac)` pair for their own store, then replay that exact body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a victim shop. `HmacValidator.validate` still succeeds because it never inspected those headers, and `Registry.process` will hand the attacker-chosen shop/topic (with the replayed body) to the app's handler as if it were an authentic event for the victim tenant.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is meant to enforce: a party with access to only their own shop's legitimate webhook traffic can attribute arbitrary already-signed payloads to a different, unrelated shop, or redirect a payload to a topic handler it was never signed for. Downstream apps built on this gem generally use `WebhookMetadata#shop` to decide which merchant record to update, so this is a cross-tenant data-integrity/access issue at the library boundary — the app has no way to detect the spoofing because the gem's own `process`/`HmacValidator` API reports the request as validly authenticated.

### Likelihood Explanation
Exploitation requires only: (1) being an app user/merchant capable of installing the app and receiving at least one real webhook for their own store, and (2) the ability to POST to the app's public webhook receiver endpoint with modified headers — both are available to an ordinary internet user/merchant with no special privileges, no access token, and no knowledge of `api_secret_key`.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body before `Registry.process` trusts them for routing/tenant attribution. At minimum, document that the gem does not authenticate these headers and that consuming apps must independently verify `shop` against expected/known values before acting on webhook data.

### Proof of Concept
1. Merchant A installs the app and legitimately receives a webhook: body `B`, `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Topic: orders/create`.
2. Attacker (Merchant A) resends the same request to the app's webhook endpoint but changes the header to `X-Shopify-Shop-Domain: shop-b.myshopify.com` (a shop they don't own), keeping body `B` and HMAC `H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` → returns `B` only, computes `HMAC(api_secret_key, B)`, and it matches `H` — validation passes.
4. `Registry.process` dispatches `WebhookMetadata.new(topic: "orders/create", shop: "shop-b.myshopify.com", body: parsed(B), ...)` to the app's handler, which believes this is a genuine event for `shop-b`, despite `shop-b` never having sent or authorized it.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L10-16)
```ruby

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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
