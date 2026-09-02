### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook HMAC and then dispatches to the app's handler using `request.shop`, but `request.shop` is read from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the HMAC-signed content. The signature only covers the raw request body.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only [1](#0-0) , while `Webhooks::Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, independent of the signed body [2](#0-1) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` and, once it passes, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler as the tenant identifier [3](#0-2) . `HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`, i.e., the raw body, and compares it with `OpenSSL.secure_compare` [4](#0-3) .

The binding this breaks, expressed as an equality that should hold but does not:
`shop_used_for_tenant_dispatch (header "shopify-shop-domain") == shop_covered_by_hmac (bytes in @raw_body)`

Since the shop-domain header sits entirely outside the HMAC's signed byte range, an attacker who can influence or replay the header (e.g., a proxy, load balancer, or any component that forwards the same signed body but rewrites/duplicates the shop-domain header before it reaches the app) can cause the library to report a different `shop` in `WebhookMetadata` while the HMAC still validates successfully against the legitimate body from another shop.

### Impact Explanation
If a host application's webhook handler uses `WebhookMetadata#shop` — as documented and expected by this gem — to select the tenant record, access token, or database scope, an attacker able to manipulate delivery headers while preserving a validly-signed body could cause the request to be attributed to a different shop, resulting in cross-tenant data association within the app. This matches the "High: cross-tenant access" category. This is entirely a consequence of the gem's `Webhooks::Request`/`Registry` design, since the gem's documented API exposes `WebhookMetadata.shop` as the authenticated tenant identifier while its own `HmacValidator` never actually authenticates that value.

### Likelihood Explanation
Exploitation requires the attacker to control or manipulate the delivery path between Shopify and the app (e.g., a shared/misconfigured webhook endpoint, reverse proxy, or replay of a captured payload with a modified header) while the HMAC-signed body remains bytes-for-bytes identical to a legitimately-signed webhook. Direct end-to-end exploitation solely against the gem's own code (with no infrastructure assumption) is limited, since a remote attacker without access to Shopify's signing key cannot alter the body; they would only be able to alter the header in a replay/relay scenario. Likelihood is therefore moderate rather than trivial, but the root cause — a tenant-identifying field left out of the HMAC-signed digest — is a concrete gap in the gem's authentication guarantee, distinct from a documented-but-ignored API misuse by the host app.

### Recommendation
Bind the shop-domain header value into the HMAC-signed content (e.g., include it in `to_signable_string`, similar to how OAuth's `AuthQuery#to_signable_string` includes `shop`), or otherwise cryptographically tie the `shop-domain` header to the signed body so `Registry.process`/`HmacValidator.validate` reject any webhook whose header-derived shop was not part of what Shopify actually signed.

### Proof of Concept
1. Shopify sends a legitimate webhook for `shop-a.myshopify.com` with body `B` and header `X-Shopify-Shop-Domain: shop-a.myshopify.com`; the HMAC is `HMAC(secret, B)`.
2. A component in the delivery path (proxy, replay, or man-in-the-middle without needing the secret) forwards the exact same body `B` and HMAC header, but rewrites `X-Shopify-Shop-Domain` to `shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only look at the raw body, so `Utils::HmacValidator.validate(request)` still returns `true` [5](#0-4) [6](#0-5) .
4. `Registry.process` calls `handler.handle` with `WebhookMetadata.new(... shop: request.shop ...)` set to the attacker-controlled `shop-b.myshopify.com` value, even though the signed payload never attested to that shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
