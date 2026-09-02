## Title
Webhook shop identity binding bypass via unauthenticated `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` covers exclusively the JSON payload bytes. None of the `X-Shopify-*` headers — including `shop-domain`, `topic`, `webhook-id`, and `api-version` — are part of the signed material, yet `Registry.process` trusts `request.shop` (derived straight from the unauthenticated header) as the tenant identity passed to the webhook handler.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Only `@raw_body` is signed. `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

This breaks the identity binding: `shop_authenticated_by_hmac == ∅ ≠ shop_used_by_handler == request.shop (header)`. Compare with the `AuthQuery` used in OAuth callback validation, where `shop` **is** included in the signed string, correctly binding the shop to the HMAC: [4](#0-3) 

The webhook path has no equivalent binding for `shop`.

### Impact Explanation
An unprivileged internet user who controls any shop that has the target app installed (e.g., a free Shopify dev/trial store) receives genuine, validly-HMAC-signed webhook deliveries for their own shop. Because the HMAC only signs the body and the app's `client_secret`/`api_secret_key` never varies per shop, that attacker can capture one such valid `(body, hmac)` pair and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds because the body/hmac pair is untouched, and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the forged victim domain. Any host application that uses `WebhookMetadata#shop` to look up per-tenant session/state (the intended and documented usage pattern) will process attacker-controlled data as if it originated from the victim's shop — e.g. spoofing `app/uninstalled` to wipe a victim's stored session, or injecting attacker-controlled `orders/*` / `customers/*` payloads keyed to the victim tenant. This is a cross-tenant confusion primitive rooted entirely in this gem's webhook verification logic, not in host misuse of an undocumented API.

### Likelihood Explanation
Any developer/merchant account can install the app on a shop they control and observe legitimate webhook deliveries; no privileged credentials, TLS interception, or social engineering are required — only a normal, unprivileged install. Forging headers on a replayed HTTP request requires no special access to Shopify's infrastructure.

### Recommendation
Include the security-relevant headers (`shop-domain` at minimum, ideally `topic` and `webhook-id`) in the signable string, or otherwise cryptographically bind them to the HMAC computation, mirroring the approach taken in `AuthQuery#to_signable_string`. Failing that, document prominently that `WebhookMetadata#shop`/`#topic` are not authenticated by the HMAC and must not be trusted for tenant-identity decisions.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `app/uninstalled`), capturing the raw body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` computed over `B` with the app's `client_secret`.
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `HmacValidator.validate(request)` returns `true` because only `B`/`H` are checked (`lib/shopify_api/utils/hmac_validator.rb:13-22`, `lib/shopify_api/webhooks/request.rb:36-38`).
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and invokes the handler, which the host app treats as an authenticated event from the victim shop.

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
