Based on the analysis, I found a valid identity-binding gap analogous to the reported bug class.

### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic for a given shop once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only covers the raw request body — never the `shop-domain` header that is subsequently trusted as the tenant identifier passed to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is derived solely from the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

`shop` is read from a completely separate, unsigned header: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop` as the tenant identity forwarded to the app's webhook handler: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated by HMAC == shop used as tenant key`. In reality, the HMAC only proves "this body+signature pair was produced with the app's `client_secret`" — it says nothing about which shop the body is for, because `client_secret` is shared by the app across *all* installing shops, not shop-specific. Since `HmacValidator.validate_signature` only compares `computed_signature` (from body) against `received_signature` (the header), the `shop-domain` header can be swapped without invalidating the signature: [5](#0-4) 

Compare this to the OAuth callback flow, where the equivalent identity field (`shop`) *is* included inside `to_signable_string` and thus is cryptographically bound to the HMAC: [6](#0-5) 

No equivalent binding exists for webhook shop identity.

### Impact Explanation
Any actor who can obtain one genuine, validly-signed webhook body+HMAC pair for their own shop (installing the app is enough to receive real webhooks addressed to them, signed with the app's shared `client_secret`) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body hash, and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the forged victim shop, causing the host application to process attacker-controlled data as if it originated from another tenant — a cross-tenant data injection / spoofing condition.

### Likelihood Explanation
Any unprivileged internet user who can install the target app on a store they control (a very low bar for public apps) automatically becomes a source of validly-HMAC-signed webhook traffic under the app's shared secret, and can trivially script header substitution against the app's public webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the material that is authenticated, or require the host application to independently reconcile `request.shop` against a shop that is known to have this specific webhook subscription/installation before trusting it as a tenant key, and document this requirement clearly. At minimum, `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` should not allow `shop` to be treated as verified data when it is never part of the signed payload.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com`.
2. Attacker triggers an `orders/create` event on their own store; Shopify delivers a webhook to the app with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's `client_secret`.
3. Attacker captures the raw body and HMAC header.
4. Attacker POSTs the identical body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this succeeds because the signature only depends on the (unchanged) body.
6. The app's registered handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, and the host application processes attacker-controlled data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
