### Title
Webhook `shop-domain` header is trusted for tenant identity but not covered by the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then unconditionally trusts the `shop-domain` (or `x-shopify-shop-domain`) HTTP header to determine which tenant the webhook belongs to. Because the header is not part of the signed material, the equality the system implicitly relies on — "shop that produced a validly-signed webhook" == "shop the handler processes the payload as" — does not actually hold.

### Finding Description
`Utils::HmacValidator.validate` is used both for OAuth callbacks and for webhooks. For OAuth, `AuthQuery#to_signable_string` includes `shop` in the signed string, so the `shop` value is cryptographically bound to the signature: [1](#0-0) 

For webhooks, however, `Webhooks::Request#to_signable_string` returns only the raw body, and the `shop` accessor reads directly from the unauthenticated `shop-domain` header: [2](#0-1) [3](#0-2) 

`Registry.process` validates only that HMAC (i.e., that the body bytes were signed with the app's `client_secret`), and then immediately dispatches to the handler using the unauthenticated `shop` field taken from the header, without any check that this shop is the one that actually produced the signed payload: [4](#0-3) 

Since a single app uses one shared `client_secret` (`Context.api_secret_key`) across every shop that has installed it, "the body bytes are validly signed by this app's secret" is true for webhooks generated for *any* installed shop — the signature says nothing about *which* shop. The `shop-domain` header is therefore acted upon by `WebhookMetadata` (and forwarded to the host app's handler as the authoritative tenant identifier) despite not being covered by the authentication check — exactly the "field acted on but not covered by the HMAC" identity-binding break called out for this analysis.

### Impact Explanation
A merchant who has installed the app (i.e., an "unprivileged" party relative to other tenants of the same multi-tenant app) can capture a legitimate webhook delivery to their own shop (raw body + `X-Shopify-Hmac-Sha256`), then replay that exact body/HMAC pair to the app's webhook endpoint with the `shop-domain`/`X-Shopify-Shop-Domain` header changed to a victim shop. `HmacValidator.validate` still succeeds because it only checks the body against the shared secret, and `Registry.process` will invoke the handler with `WebhookMetadata.new(... shop: request.shop ...)` pointing at the victim shop. If the host application uses `data.shop` to select which tenant's records to create/update/delete (the documented and expected usage pattern per `docs/usage/webhooks.md`), this results in cross-tenant data injection/corruption — data belonging to the attacker's own shop is written into another merchant's tenant context.

### Likelihood Explanation
Requires only: (1) the attacker installs the app on their own shop (or otherwise legitimately receives a webhook for their shop) so they have one valid body+HMAC pair, and (2) the ability to send an HTTP request to the app's public webhook endpoint with a forged header — no privileged credentials, access tokens, or knowledge of `client_secret` are needed. This is reachable by any unprivileged internet user who is (or becomes) a merchant of the multi-tenant app.

### Recommendation
Bind the shop identity into the authenticated material, or otherwise verify it out-of-band, before trusting `request.shop`:
- Include the `shop-domain` header value in `to_signable_string` for webhook requests, or
- Require the host application (and document it clearly) to independently verify that `request.shop` corresponds to a shop with a currently registered/active webhook subscription for that specific `webhook_id`/`topic` before acting on the payload, or
- Cross-check the `shop` header against a per-shop webhook secret if using Shopify's newer per-shop webhook signing, if available.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, sharing one `Context.api_secret_key`.
2. Attacker triggers an event on their own shop (e.g., `orders/create`) and captures the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` sent by Shopify to the app's webhook endpoint.
3. Attacker replays:
```
POST /callback/orders/create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Body: B
```
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds `shop == "victim-shop.myshopify.com"`.
5. `Utils::HmacValidator.validate(request)` succeeds because `H` truly signs `B` with the shared `client_secret`.
6. `Registry.process` calls the handler with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, so the host app processes attacker-controlled order data as though it belongs to the victim's store.

### Citations

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
