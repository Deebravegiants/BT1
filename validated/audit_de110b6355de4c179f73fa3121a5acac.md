# Title
Webhook Tenant Spoofing — HMAC Covers Only the Raw Body, Not the `shop-domain` Header, Enabling Cross-Tenant Webhook Impersonation - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw HTTP body only, while the tenant-identifying `shop` value is read from an unsigned HTTP header. `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` handed to the application's webhook handler. Because the header carrying the shop identity is never covered by the HMAC, a party who can obtain one genuinely signed webhook body/HMAC pair (e.g., by installing the app on their own store) can relabel it with an arbitrary victim `shop-domain` and have it accepted as authentic, causing cross-tenant data confusion in the host application.

### Finding Description
`AuthQuery#to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:33-43`) deliberately signs `code`, `host`, `shop`, `state`, and `timestamp` together, so the shop identity is bound to the signature for OAuth callbacks: [1](#0-0) 

In contrast, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are outside the signed content: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which — via `VerifiableQuery`/`Request#to_signable_string` — only proves the *body bytes* were signed by the app's secret. It then immediately forwards `request.shop` (an unauthenticated header) into `WebhookMetadata`, which is the tenant identifier the host application's handler acts on: [3](#0-2) 

The equality that should hold is:
`shop bound inside the HMAC-signed content == shop the handler uses to attribute the webhook`

Instead, the gem enforces only:
`HMAC(secret, raw_body) == received_hmac`, and separately trusts `headers["shopify-shop-domain"]` verbatim.

This mirrors the bug class in the report: a field (`shop`) that is acted upon (tenant attribution in `WebhookMetadata`) but not covered by the authenticity check (`HmacValidator` only signs the body).

### Impact Explanation
An unprivileged internet user can install the target app on their own (free/dev) Shopify store — no privileged credentials are required — and trigger any webhook topic the app subscribes to (e.g. `orders/create`, `customers/update`) with attacker-chosen body content. Shopify will deliver this webhook with a body and an HMAC that is genuinely valid for the app's secret. The attacker then replays that exact `(raw_body, hmac)` pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to a victim shop's domain. Because `HmacValidator.validate` never inspects the header, `Registry.process` accepts the request as authentic and delivers `WebhookMetadata` claiming the (attacker-authored) body belongs to the victim shop. Any host application logic keyed off `data.shop` (e.g., updating per-tenant records, triggering per-tenant side effects) can be corrupted with attacker-controlled data attributed to a shop the attacker does not own — a cross-tenant confusion/impersonation impact.

### Likelihood Explanation
Likelihood is moderate-to-high for apps that trust `WebhookMetadata#shop` as an authenticated tenant identifier (a very common pattern, since this is exactly the field the gem exposes for that purpose). The only requirement is the ability to install the app on any store and to send an HTTP POST with custom headers to the app's public webhook endpoint — both achievable by any unprivileged actor. No access token, `client_secret`, or account privilege escalation is needed.

### Recommendation
Bind the tenant-identifying headers into the HMAC-checked content (e.g., include `shop`, `topic`, and `webhook_id` in the signable string, similar to how `AuthQuery` binds `shop`/`host`/`state`), or otherwise cryptographically tie the header values to the signed payload before exposing them via `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be independently cross-checked by the host application (e.g., against a shop the app knows it has installed) before being trusted.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a subscribed webhook topic (e.g., updates an order) so Shopify sends a POST with body `B` and header `Shopify-Hmac-Sha256: H` (a valid HMAC of `B` under the app's real secret), along with `Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and resends it to the app's webhook endpoint, keeping body `B` and header `H` unchanged but replacing the shop header with `Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body as usual; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation passes.
5. `handler.handle` receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and the host app processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`. [4](#0-3) [5](#0-4)

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
