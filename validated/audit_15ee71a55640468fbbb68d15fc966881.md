### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` validates a webhook's authenticity by computing an HMAC over the raw request body only, while the `shop` (tenant identifier), `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Registry.process` accepts the request as long as the body-HMAC matches, then dispatches the handler using the header-derived `shop` value with no binding between the signed bytes and the tenant identity.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is defined as just the raw body: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are pulled straight from HTTP headers, which are never part of the signable string: [2](#0-1) 

`Registry.process` only checks the body HMAC, then immediately trusts `request.shop` as the tenant for the dispatched handler data: [3](#0-2) 

Because the HMAC secret (`Context.api_secret_key`) is shared across all shops using the app (it's the app's `client_secret`, not a per-shop secret) and the signature covers only the body, any party in possession of one valid `(raw_body, hmac)` pair — trivially obtainable by any merchant who has the app installed and receives real webhook deliveries from Shopify to their own endpoint — can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header to name a different, victim shop. The equality that should hold, `shop_bound_by_signature == shop_used_for_tenant_dispatch`, is broken: the signature binds only the body bytes, not the shop field acted upon.

This is exactly the class of bug flagged in the external report: a value (`shop`) is acted on by privileged logic (tenant dispatch) without being covered by the integrity check (HMAC) that gates access.

### Impact Explanation
An attacker who legitimately installed the app on their own shop (or otherwise obtains one valid signed webhook body, e.g. for topics with static/empty bodies like `app/uninstalled` `{}`) can forge webhook events that the host application will process as coming from an arbitrary victim shop. Since host apps commonly use `WebhookMetadata#shop` to look up/mutate per-tenant state (uninstall app data, disable subscriptions, update tenant records, etc.), this enables cross-tenant data manipulation — data belonging to shop B is altered/deleted based on a forged request purporting to be from shop B, injected by an attacker who only controls shop A. This satisfies the "cross-tenant access" High-impact criterion.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to obtain at least one genuinely-signed `(body, hmac)` pair, which is trivial for any merchant with the app installed (they receive real webhooks to their own callback URL and can capture the raw POST). No access to `api_secret_key` or an access token is needed — only a replay of already-delivered ciphertext-adjacent HTTP payloads with a header swap.

### Recommendation
Include the tenant-identifying header(s) (`shop`, and ideally `topic`/`webhook_id`) in the signable string used for HMAC validation, or otherwise cryptographically bind the shop domain to the signed payload before trusting `request.shop` for dispatch. At minimum, document/require that host applications independently verify `request.shop` corresponds to a shop with an active, known installation/session before acting on the webhook.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook, e.g. topic `app/uninstalled` with body `"{}"` and a valid `x-shopify-hmac-sha256` header (computed by Shopify using the app's real `client_secret`).
2. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `@raw_body` via `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`), which is unchanged.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the handler with `shop: request.shop == "victim-shop.myshopify.com"`, causing the host app to perform tenant-scoped actions (e.g., wiping victim's app data) attributed to the victim shop.

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
