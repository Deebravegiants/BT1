## Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw request body via HMAC, but the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the host application's handler come from unauthenticated HTTP headers. This breaks the identity binding `hmac-signed bytes == fields acted upon`, allowing a party who possesses one valid `(body, hmac)` pair for the shared app secret to relabel that payload as belonging to an arbitrary victim shop.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, and for webhook requests that method returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and the other header-derived fields) when constructing the `WebhookMetadata` passed to the app's handler, without any additional binding check: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no relationship enforced to the HMAC-covered body: [4](#0-3) 

The equality that should hold is: `shop value the HMAC vouches for == shop value delivered to the handler`. Because the HMAC is computed only over `@raw_body`, this equality is never enforced — the gem verifies "these bytes were authored by someone holding the app secret" but the handler is told "these bytes belong to shop X" purely from an unauthenticated header. Since the HMAC secret (`client_secret`) is shared across every shop that installs the app, any merchant who has installed the app can capture one legitimately-signed webhook body/HMAC pair delivered to their own endpoint and replay it to the app's public webhook callback URL with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a different, victim shop domain. `HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity-confusion vector: the host application's webhook handler (per the gem's documented usage in `docs/usage/webhooks.md`, which explicitly tells implementers to trust `data.shop` to route/attribute the webhook, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) receives attacker-controlled tenant attribution for a body it correctly believes originated from a legitimate installer. Depending on how the host app uses `data.shop` (e.g., looking up a session/access token, writing records, triggering per-shop side effects), this enables cross-tenant data confusion/access — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own legitimate app installation (any merchant can install a public app), which lets them observe genuine `(body, hmac)` pairs signed with the shared `client_secret`, and (2) the ability to POST to the app's public webhook endpoint with a forged `shop-domain` header — no possession of `client_secret`, access tokens, or privileged access is required. This is a purely unauthenticated-internet-request scenario against the gem's own verification logic.

### Recommendation
Bind the shop identity into the authenticated material before it is trusted: either include the `shop-domain` (and ideally `topic`/`webhook_id`) headers in the signable string used by `HmacValidator`, or require `Registry.process` to cross-check `request.shop` against an independently verified value (e.g., the shop associated with the webhook subscription that was registered, looked up via `webhook_id`) before constructing `WebhookMetadata`. At minimum, update `docs/usage/webhooks.md` to warn implementers that `data.shop` is unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker configures a webhook handler endpoint they control and observes a legitimate Shopify webhook delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC over `B` with the shared `client_secret`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `B` and `H` to the target app's public webhook callback route, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` proceeds: [3](#0-2) 
4. The host handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the body content and its authenticated signature came from `attacker-shop.myshopify.com`, causing the body to be processed/attributed under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
