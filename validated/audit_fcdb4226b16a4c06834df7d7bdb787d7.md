Based on my investigation, I have enough evidence to finalize the analog vulnerability.

### Title
Webhook shop-domain and topic identity not covered by HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` fields—used by `Registry.process` to identify which merchant/tenant and action a webhook belongs to—are read directly from unauthenticated HTTP headers. This mirrors the reported `SecuritizeSwap.buy()` flaw: a value that drives a tenant/identity-bound action (`_investorWallet` in the report, `shop`/`topic` here) is not covered by the same validation that protects the sibling code path (the wallet-ownership check in `swap()`, the HMAC-over-headers a reasonable implementation would need here).

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`. For webhooks, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are read straight from headers, none of which participate in the signature: [2](#0-1) 

`Registry.process` trusts these header-derived values to identify the tenant and dispatches the handler using `request.shop` and `request.topic` without any additional cross-check against the signed body: [3](#0-2) 

The broken binding, expressed as an equality that should hold but doesn't:
`shop header used to attribute the webhook == shop the HMAC secret was actually signed for`. Because `Context.api_secret_key` is the same for every shop that installs the app, any shop that legitimately installs the app receives genuinely HMAC-signed webhook deliveries (body + valid signature) for its own store. An attacker who controls such an installation can capture a valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop, and/or the `X-Shopify-Topic` header rewritten to a different (attacker-chosen) topic. `HmacValidator.validate` still succeeds because the signature only ever certified the body bytes, not the header bytes that `Registry.process` uses to decide "who this event is about" and "what to do."

This is the same class of defect as the report: verification covers one part of the state (the raw bytes / one field) while the code acts on an adjacent, unguarded field for identity/authorization purposes (shop attribution / wallet ownership).

### Impact Explanation
An attacker with any legitimate shop installation of a vulnerable host app can forge webhook events attributed to a victim shop by replaying a self-obtained signed body under a spoofed `shop-domain`/`topic` header pair, since `Registry.process` and `WebhookHandler.handle` receive `shop: request.shop` unauthenticated. Depending on how the host app's handler uses `WebhookMetadata.shop` (e.g., to key data deletion, mark uninstall/redact, or update per-tenant records), this enables cross-tenant data corruption or triggers privileged per-tenant actions (such as GDPR redact/uninstall workflows) against a shop the attacker does not control — a cross-tenant impact.

### Likelihood Explanation
Moderate-to-high: the primitive only requires the attacker to install the app on any shop they control (a normal, unprivileged action) and to be able to send arbitrary HTTP requests to the app's public webhook endpoint with attacker-chosen headers — both are available to an ordinary internet user/merchant, no `api_secret_key` or leaked credentials required.

### Recommendation
Include the identity fields that are used for tenant attribution and dispatch (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the HMAC-signable representation, or otherwise cryptographically bind them to the verified body (e.g., require them to be embedded/hashed within the signed payload the way Shopify's webhook payload can carry `shop_id`/`shop_domain` fields), and cross-check the header value against that bound value before trusting `request.shop`/`request.topic` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (legitimate, unprivileged onboarding).
2. Shopify delivers a real webhook, e.g. `orders/create`, to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's `client_secret`.
3. Attacker captures `(raw_body, hmac_header)`.
4. Attacker resends an HTTP POST to the same webhook endpoint with the identical `raw_body`/`hmac` but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`, e.g. `customers/redact`).
5. `Webhooks::Request.new` parses these headers unchanged; `HmacValidator.validate(request)` succeeds because it only checks `@raw_body` against the secret — it never inspects the headers: [4](#0-3) 
6. `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"`, causing the host app to act as though the event genuinely originated from the victim tenant.

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
