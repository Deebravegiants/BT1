### Title
Webhook Cross-Tenant Spoofing via Unsigned `shop-domain` / `topic` Headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` to attribute and route the event are taken directly from unauthenticated HTTP headers. Because the app's webhook signing secret (`Context.api_secret_key`) is shared by every shop that installs the same app, any merchant who has installed the app can legitimately trigger and capture a validly-signed `(body, hmac)` pair for their own shop, then resend it to the app's webhook endpoint with a forged `shopify-shop-domain` (and/or `shopify-topic`) header claiming to belong to a different tenant shop. The signature still validates because it never covered those header values, letting an unprivileged app-installer inject events attributed to another merchant.

### Finding Description
`Request#hmac` and `Request#to_signable_string` only bind the HMAC to the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors simply read attacker/network-supplied headers with no cryptographic tie to the signature: [2](#0-1) 

`HmacValidator.validate` recomputes the signature strictly from `to_signable_string` (the body) using the single, app-wide `Context.api_secret_key` (shared across all shops that installed the app), and does not incorporate the `shop` header into the signed material: [3](#0-2) 

`Registry.process` trusts this unauthenticated `request.shop` value to build the event metadata handed to the app's business logic, which typically uses `shop` as the tenant identity key: [4](#0-3) 

The identity binding broken is: `HMAC-authenticated-secret-owner == shop-in-header`. In reality, the HMAC only proves "signed with this app's shared secret" (true for a request about *any* shop that installed the app), not "signed specifically for shop X". A merchant with the app installed knows the app's webhook secret is not directly exposed to them, but they *can* obtain a valid `(raw_body, hmac)` pair for their own shop's real events (e.g., by creating an order in their own store and capturing the resulting webhook delivery), and then replay that exact pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` will still pass because it never checked the header, and `Registry.process` will dispatch the handler with `shop: <victim-shop>`.

### Impact Explanation
This breaks the tenant boundary the app relies on to attribute webhook events to the correct merchant. Any single installer of a multi-tenant app can forge webhook deliveries that are processed as if they came from another arbitrary shop domain, enabling cross-tenant data injection/spoofing (e.g., fake `orders/create`, `app/uninstalled`, or `customers/redact` events attributed to a victim shop) purely with knowledge of a shop domain string — which is public. This matches the Critical "cross-tenant access" impact category, since the identity used to route/authorize per-tenant business logic downstream of this library is not actually authenticated.

### Likelihood Explanation
Likelihood is high for any app that has more than one shop installed (the common case for a public app): the attacker needs only (1) to be an installer of the app on their own shop (an unprivileged action, e.g., a free trial install) to receive at least one legitimately signed webhook body+HMAC pair, and (2) network access to POST that pair to the app's public webhook endpoint with a different `shop-domain` header. No access to `api_secret_key`, tokens, or the target shop is required.

### Recommendation
Bind the shop identity to the signature verification, for example:
- Include `shop`, `topic`, and other routing-relevant headers in the signable content computed by `to_signable_string`, and require the payload's signature to cover them, or
- Independently verify that the shop domain reported in the webhook actually matches the shop referenced inside `parsed_body` where applicable, or maintain a per-shop mapping and require the `shop` header to be cross-checked against session/install records before trusting it for tenant attribution, rather than trusting the header value as-is in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers a real event (e.g., creates an order) causing Shopify to deliver a legitimately-signed webhook to the app's endpoint with headers:
   - `shopify-topic: orders/create`
   - `shopify-hmac-sha256: <valid HMAC of raw body using app secret>`
   - `shopify-shop-domain: attacker.myshopify.com`
3. Attacker captures the raw body and the `shopify-hmac-sha256` value (both fully visible to them since it's their own webhook, e.g., via a debug proxy).
4. Attacker replays the identical `raw_body` and `shopify-hmac-sha256` to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body's HMAC (line 12-31 of `hmac_validator.rb`), and then invokes the app's handler with `shop: "victim-shop.myshopify.com"` (line 198 of `registry.rb`), causing the app to process/attribute the forged event to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
