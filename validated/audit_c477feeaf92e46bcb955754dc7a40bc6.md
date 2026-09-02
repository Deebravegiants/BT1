### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing on replayed webhooks - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while the `shop` identity used by `Registry.process` to route data to a tenant is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header [2](#0-1) . The HMAC therefore proves "this body was signed by Shopify with the app's secret" but never proves "this body belongs to this shop."

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`, which for webhooks is only `@raw_body` [3](#0-2) . The `shop`, `topic`, `api_version`, and `webhook_id` values are all pulled straight from HTTP headers that are excluded from the signed content [4](#0-3) .

`Registry.process` validates only the HMAC of the body, then immediately trusts the header-derived `request.shop` as the tenant identity and forwards it to the app's handler as verified metadata: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [5](#0-4) .

The broken identity binding, as an equality that should hold but doesn't:
`shop_bound_by_hmac(raw_body) == shop_used_for_tenant_routing(header)`

Before the attack: a merchant who installs the app on their own store (e.g. `attacker-shop.myshopify.com`) legitimately receives a real Shopify-signed webhook — genuine `raw_body` and genuine `X-Shopify-Hmac-Sha256` computed by Shopify with the app's secret, plus header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.

After the attack: the attacker replays the exact same `raw_body` (so the HMAC still validates, since HMAC covers only the body) but swaps the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`. `HmacValidator.validate` still returns `true` because it only checks body integrity/authenticity, not the header. `Registry.process` then hands the handler a `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` with attacker-controlled body content, `topic`, and `webhook_id` values that the app never independently verifies.

### Impact Explanation
Any host application that uses the library's `WebhookMetadata#shop` as the authoritative tenant key (the natural and encouraged usage, since the library exposes it as a verified-looking field right after `HmacValidator.validate` succeeds) can be made to write, delete, or process data under the wrong shop's tenant scope — i.e., cross-tenant access/data corruption, using only a legitimately-installed low-privilege app instance as the attack vector. No `api_secret_key`, access token, or privileged account is required beyond the attacker's own (self-service, free) shop installation, which is the "unprivileged internet user" baseline for this analysis.

### Likelihood Explanation
Likelihood is realistic: any developer/attacker can install a public embedded app on their own Shopify development store, capture a real webhook delivery to their endpoint, and replay it with a modified `shop-domain` header, since this header is neither part of the signed payload nor re-validated by the library. The library's own `Registry.process` does not raise or warn in this case — the mismatch is completely silent.

### Recommendation
Bind the shop identity to the signed content, or require the caller to supply/verify the expected shop out of band before trusting `WebhookMetadata#shop`. Concretely: include `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-covered signable string, or require `Registry.process` to accept an expected shop/tenant parameter and assert it matches `request.shop` before invoking the handler, rather than trusting the header value as verified.

### Proof of Concept
1. Install a test app on `attacker-shop.myshopify.com` and trigger a webhook (e.g., `orders/create`) to the app's webhook endpoint. Capture the raw POST: body `B`, and headers including a genuine `X-Shopify-Hmac-Sha256: H` (valid because `HMAC(secret, B) == H`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Replay the identical request to the same endpoint, only changing `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, keeping body `B` and `X-Shopify-Hmac-Sha256: H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: replayed_headers)` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only compares `B` against `H` [1](#0-0) .
4. `ShopifyAPI::Webhooks::Registry.process(request)` succeeds and calls the app's handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and attacker-chosen `body`, despite the payload never having been produced or signed for that shop [5](#0-4) .

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
