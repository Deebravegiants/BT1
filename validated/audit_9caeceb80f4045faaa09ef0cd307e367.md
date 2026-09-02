### Title
Webhook `shop-domain` header is trusted for tenant attribution while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw request body only, but exposes `shop` (tenant identity) by reading it directly from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the signed payload. `Registry.process` verifies the HMAC and then hands the *unauthenticated* `shop` value straight to the app's `WebhookHandler` as the tenant identifier for the webhook.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the HMAC: [2](#0-1) . `Registry.process` validates only the HMAC over the body and then constructs `WebhookMetadata` using `request.shop` from the header, passing it to the app-supplied handler as the trusted tenant: [3](#0-2) .

The equality the library implicitly promises to the host app is: `HMAC-verified sender == request.shop`. In reality the HMAC only proves "the body bytes were signed with the app's `client_secret`" (shared across every shop that installed this app); it says nothing about which shop's header value accompanies that body, since the header is attacker-controlled transport metadata, not signed data (`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string`, i.e. `@raw_body`: [4](#0-3) , [1](#0-0) ).

Because a single app's `client_secret` is shared across every merchant that has installed it, any merchant (an unprivileged, otherwise unauthenticated user with respect to other tenants) who has installed the app can legitimately trigger events that produce validly-HMAC'd webhook bodies for their own shop, then replay that request body while substituting the `X-Shopify-Shop-Domain` header for a different victim shop that also has the app installed. The HMAC check still passes (it only verifies the body/secret pairing), but `Registry.process` will hand the handler `WebhookMetadata.shop` = the attacker-chosen victim shop, while `body` actually belongs to the attacker's own shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the field the host application uses to select which merchant's data/session/database row to act on (`shop`) is not the field that was cryptographically verified (only `@raw_body` was). Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g., to look up a session/access token, or to route/mutate per-tenant data), an attacker can cause the app to associate their own webhook payload with another tenant's shop domain, i.e. cross-tenant data confusion/injection under a spoofed tenant identity. This matches the "cross-tenant access" Critical-impact category defined by the assessment rules.

### Likelihood Explanation
Exploitability requires: (1) the attacker controls or can trigger a legitimately-signed webhook for at least one shop that has the app installed (any merchant/uninstall-reinstall or self-triggered event, e.g. `app/uninstalled`, `orders/create` in their own store), and (2) the ability to send an arbitrary HTTP request with modified headers to the app's public webhook endpoint, which is inherent to how webhook endpoints work (they are unauthenticated inbound endpoints identified only by HMAC + headers). No access token, `api_secret_key`, or privileged account is required by the attacker; they only need to be a normal merchant of the multi-tenant app. This is a realistic, moderately likely path for any multi-tenant Shopify app using this gem's webhook verification/registry as documented.

### Recommendation
Bind `shop` (and ideally `topic`, `webhook_id`, `api_version`) into the HMAC-covered signable string, or otherwise require the host application to separately verify that the `shop-domain` header matches a shop that is expected to be sending this particular signed body (e.g., pass the expected shop into `HmacValidator.validate`/`Request` and fail closed if it doesn't match a shop the app actually manages, rather than trusting the header unconditionally after only body-HMAC validation).

### Proof of Concept
1. App `A` is installed on shop `victim.myshopify.com` and shop `attacker.myshopify.com`, sharing one `client_secret`.
2. Attacker triggers a webhook-eligible event on their own `attacker.myshopify.com` store (e.g., updates an order), capturing the resulting webhook `POST` with a valid `X-Shopify-Hmac-Sha256` header computed over the raw body.
3. Attacker replays this exact request to the app's webhook endpoint but rewrites the `X-Shopify-Shop-Domain` header to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks the raw body against `client_secret` [4](#0-3) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.shop == "victim.myshopify.com"` while `body` is the attacker's own order data [5](#0-4) , causing the host app to process/attribute the payload under the victim tenant's identity.

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
