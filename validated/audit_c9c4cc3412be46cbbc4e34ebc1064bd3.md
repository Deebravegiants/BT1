### Title
Webhook shop-domain header trusted despite not being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values consumed and handed to the app's webhook handler come from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all read straight from `@headers` with no cross-check against the signed body [2](#0-1) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` and, once that body-only check passes, immediately builds `WebhookMetadata` from the header-derived `request.shop`, `request.topic`, and `request.webhook_id`, handing it to the app's handler [3](#0-2) . `HmacValidator.validate` itself only compares `verifiable_query.to_signable_string` against the secret [4](#0-3) , so the binding `hmac(body) == hmac_header` never establishes `shop_header == shop_that_produced(body, hmac)`.

This differs materially from `ShopifyAPI::Auth::Oauth::AuthQuery`, where the analogous "identity" field (`shop`) *is* folded into `to_signable_string` and thus cryptographically bound to the HMAC [5](#0-4) . The webhook `Request` class has no equivalent binding for `shop-domain`, `topic`, or `webhook-id`.

### Impact Explanation
An unprivileged internet user who legitimately owns any Shopify store can install the app under test, trigger any webhook event, and capture a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's real secret. Because the HMAC never binds to the `x-shopify-shop-domain` header, that same captured body+HMAC pair remains valid when replayed to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. `Registry.process` will accept the forged HMAC and dispatch `WebhookMetadata` claiming the (attacker-chosen) body originated from the victim tenant. Any host application that uses `WebhookMetadata#shop` to select the tenant record to mutate (the intended and expected use, since `Registry.process` is this gem's documented processing entry point) will apply attacker-controlled webhook data under the wrong tenant, i.e. cross-tenant data injection/spoofing.

### Likelihood Explanation
Requires only the ability to run a Shopify webhook once for an attacker-controlled shop (trivial — free development stores are attacker-obtainable) and direct HTTP access to the target app's public webhook endpoint. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material `to_signable_string` returns, or otherwise cryptographically bind them to the payload before validating, mirroring the approach already used in `AuthQuery#to_signable_string`. At minimum, document that consumers of `Registry.process`/`WebhookMetadata` must independently verify `shop` against their own registered-shop list before trusting the payload for that tenant.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw JSON body `B` and the valid `x-shopify-hmac-sha256: H` header computed with the real API secret over `B` (per `Request#to_signable_string`, `lib/shopify_api/webhooks/request.rb:35-38`).
2. Attacker POSTs the same `B` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`, keeping `x-shopify-hmac-sha256: H`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H`, so `Registry.process` proceeds (`lib/shopify_api/webhooks/registry.rb:188-190`).
4. `WebhookMetadata` is built with `shop: "victim-shop.myshopify.com"` even though `B` was never produced for that shop, and is passed to the app's handler (`lib/shopify_api/webhooks/registry.rb:198-199`), completing the cross-tenant spoof.

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
