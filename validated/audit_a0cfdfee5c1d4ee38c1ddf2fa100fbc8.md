### Title
Webhook `shop`/`topic` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers and are never part of the signed bytes. `ShopifyAPI::Webhooks::Registry.process` still uses `request.shop` (and `request.topic`) to dispatch the webhook to a handler, trusting these unauthenticated header values as if they were verified. This breaks the identity binding: `bytes verified != bytes acted on`.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, `#api_version` are parsed from headers, independent of the HMAC: [2](#0-1) 

`HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC header: [3](#0-2) 

`Registry.process` validates the HMAC, then unconditionally trusts `request.shop` and `request.topic` to look up a handler and construct the metadata handed to the app's business logic: [4](#0-3) 

Because the HMAC only binds the body bytes, any caller who possesses a single valid `(raw_body, hmac)` pair for the app's shared `client_secret` (e.g., obtained from a webhook Shopify legitimately delivered for the attacker's own shop, which they installed the app on) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` passes the attacker-chosen `shop` value straight to the handler as `WebhookMetadata#shop`: [5](#0-4) 

This is the exact "field acted on but not covered by the HMAC" identity-binding break called out in scope: the equality that should hold is `hmac_signed_bytes == acted_on_identity_bytes`, but here `hmac_signed_bytes = raw_body` while `acted_on_identity_bytes = raw_body + shop_header`, so the shop identity is unauthenticated.

### Impact Explanation
Multi-tenant apps built on this gem typically use `WebhookMetadata#shop` to resolve which merchant/session a webhook event applies to (look up the shop's stored session, apply/persist the event data, etc.). Since Shopify signs webhooks with the app's single shared `client_secret` (not a per-shop secret), any merchant who installs the app can capture one valid `(body, hmac)` pair from their own store's webhook deliveries and reuse it against the same endpoint with a different `shop` header, causing the app to process/attribute data intended for one tenant to another tenant. This crosses a tenant boundary using only a header value that the app implicitly trusts because `HmacValidator` returned `true`, satisfying the "cross-tenant access" Critical impact criterion.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that (a) installs on multiple shops, and (b) uses `request.shop`/`WebhookMetadata#shop` for authorization or tenant selection without independently cross-checking it (e.g., against the topic-specific expected shop, or a separately verified session). No credentials beyond a normal app install (unprivileged, self-service) are needed to capture a valid signed payload; the attacker only replays their own legitimately-received webhook with a modified header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed content, or, since Shopify's real signature only ever covers the raw body, have `Registry.process` (or its documentation) explicitly require and demonstrate that consumers must independently verify `request.shop` against a known/expected shop for the topic (e.g., matching it against the session used to register the webhook) before trusting it for tenant-scoped logic. At minimum, the library should clearly document that `request.shop`/`request.topic` are **not** cryptographically authenticated by `HmacValidator.validate` and must not be used as a sole tenant identifier.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and lets Shopify deliver a legitimate webhook, capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header `H` (valid because `H = HMAC(client_secret, B)`).
2. Attacker sends a new POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`: unchanged or changed to another registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and compares to `H` — this succeeds since `B` and `H` are unchanged. [6](#0-5) 
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the app to process attacker-controlled body data as if it originated from the victim shop. [7](#0-6)

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
