This confirms the vulnerability: the `handle` callback exposes `data.shop` (from the unsigned `x-shopify-shop-domain` header) directly to the app's business logic, and the docs' own example (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`) shows apps are expected to trust this field for tenant routing (e.g., looking up which merchant's job queue/session to use), while the actual HMAC only signs the raw JSON body.

### Title
Webhook shop/topic/webhook-id identity is unauthenticated, allowing cross-tenant webhook spoofing via HMAC/body replay - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`, but `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values — all read straight from HTTP headers — are never included in the signed content, yet they are passed unmodified into `WebhookMetadata` and handed to the app's `handler.handle` callback as trusted identifiers.

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field [1](#0-0) . For webhooks, `to_signable_string` is defined as just the raw body bytes [2](#0-1) , while `shop`, `topic`, and `webhook_id` are parsed independently from headers with no cryptographic binding to the signature [3](#0-2) .

`Registry.process` only checks the HMAC and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata`, which is passed to the app's handler as authoritative tenant/topic identity [4](#0-3) .

Because `api_secret_key` is the app's single `client_secret`, shared across every shop that installs the app (not a per-shop secret), any body+HMAC pair that is valid for one shop's webhook is also a valid HMAC for that same body under a different `shop-domain` header. This breaks the intended binding:
`shop asserted in header == shop whose data was actually signed`.

An attacker who legitimately installs the app on their own shop receives genuine webhooks (valid body + HMAC, computed with the app's shared secret). They can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header claiming to be a victim shop. `Utils::HmacValidator.validate` still succeeds, because it never checks `shop`/`topic` against anything, and `Registry.process` calls `handler.handle` with `WebhookMetadata.shop` set to the attacker-chosen victim domain [5](#0-4) .

The library's own documentation confirms host apps are expected to key business logic (e.g., job routing, per-shop state updates) directly off `data.shop` without further verification [6](#0-5) .

### Impact Explanation
This is a cross-tenant identity-binding break: data that legitimately belongs to (and was authenticated for) shop A can be injected into the application's processing pipeline while asserting it belongs to shop B, since `shop` is "verified" (via the HMAC-approved request) but not "acted on" consistently — the field acted on (`request.shop`) is never covered by the HMAC that gates the request. This can lead to another merchant's webhook body/topic being attributed to and processed under a victim shop's tenant context, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only an unprivileged attacker who can install the app on their own shop (a normal, unprivileged action for any public app) to obtain a valid `(raw_body, hmac)` pair, and the ability to send arbitrary HTTP headers to the app's public webhook endpoint — no `api_secret_key`, access token, or privileged account is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed content verified by `Request#to_signable_string` (or otherwise cryptographically bind these header values before trusting them), rather than relying on the raw body alone to authenticate the entire request context.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H` (valid HMAC of `B`).
2. Attacker replays the identical `B` and `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged `shop` header [7](#0-6) .
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [8](#0-7) .
5. `Registry.process` calls `handler.handle` with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` [5](#0-4) , causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
