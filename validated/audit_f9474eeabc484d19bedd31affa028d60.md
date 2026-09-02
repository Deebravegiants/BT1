### Title
Webhook Shop-Domain Header Spoofing via Cross-Tenant HMAC Replay — Shop Identity Not Bound to Signed Payload - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC that covers only the raw request body, yet it hands the caller-supplied `x-shopify-shop-domain` header — which is *not* part of the signed material — to the handler as the trusted tenant identifier. An attacker who legitimately controls one shop (with the app installed) can capture one of their own genuinely-signed webhooks and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, producing a request that passes signature verification but is attributed to the wrong tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (the raw body) and the app secret, and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` relies solely on this body-only HMAC check, and then reads the tenant identity straight from the unauthenticated `shop-domain` header via `request.shop`: [3](#0-2) 

`request.shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to the body or HMAC: [4](#0-3) 

The identity binding that should hold is: `hmac-authenticated bytes == bytes used to determine tenant (shop)`. Here it does not — the HMAC only authenticates `@raw_body`, while `shop` (the tenant key handed to `WebhookMetadata` and ultimately to the app's handler) comes from a header outside the signed scope. Any request with a body+HMAC pair that was legitimately produced for shop A can be replayed with the `shop-domain` header rewritten to shop B, and `HmacValidator.validate` will still return `true` because it never inspects headers.

### Impact Explanation
This breaks a tenant/authentication boundary: a genuinely-signed webhook payload (e.g., an order or customer payload from the attacker's own shop, obtained because the attacker installed the app on their own store) can be re-submitted to the app's webhook endpoint claiming to originate from a different (victim) shop. Since `WebhookMetadata.shop` is what applications use to route/store webhook data per-tenant, this enables cross-tenant data confusion/injection — data that is really the attacker's own is processed under the victim's shop context. This matches the "cross-tenant access" Critical-impact category, since the HMAC verification (the only cryptographic control in the library for this flow) is bypassed for the purpose of tenant attribution without needing `api_secret_key`, an access token, or any privileged account.

### Likelihood Explanation
An attacker only needs to be a merchant who has installed the app (an unprivileged actor relative to other tenants) to obtain at least one genuinely-signed webhook body+HMAC pair for their own shop. Replaying that captured HTTP request with a modified `shop-domain` header against the app's public webhook endpoint requires no secrets and no interaction with Shopify's servers, making this readily reachable by any internet user in a multi-tenant deployment.

### Recommendation
Bind the shop identity into the authenticated material, or otherwise cryptographically verify it: e.g., include the `shop-domain` (and `topic`) header value in `to_signable_string`/the HMAC computation (matching how the shop is embedded and covered by HMAC in `Auth::Oauth::AuthQuery`, see `lib/shopify_api/auth/oauth/auth_query.rb`), and/or cross-check `request.shop` against the shop stored for the session/subscription that the webhook was registered for before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a webhook event (e.g., updates an order), receiving a POST from Shopify with a valid `x-shopify-hmac-sha256` computed over the raw JSON body using the app's real secret.
2. Attacker captures this raw request (body + headers).
3. Attacker resends the identical body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replaces `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `@raw_body` — unaffected by the header change — and passes.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: request.shop, ...)`, where `request.shop` now returns `"victim.myshopify.com"`, causing the app to process/store the attacker's payload under the victim's tenant.

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
