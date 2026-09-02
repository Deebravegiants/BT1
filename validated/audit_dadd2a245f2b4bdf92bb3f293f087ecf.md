### Title
Webhook shop-domain identity spoofing via HMAC scope gap — cross-tenant webhook confusion - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw JSON body, but the `shop` identity that the gem then hands to the merchant's `WebhookHandler` is read from an HTTP header that is never included in that HMAC computation. This is the same class of bug as the reported `permit` issue: a value that is validated (the signed amount / signed bytes) is not the same value that is subsequently acted upon (the mutated amount / the shop header).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values used elsewhere are all pulled from HTTP headers, which are completely outside the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies exactly and only `to_signable_string` (the raw body) against the HMAC header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust the entire `Request`, including `request.shop`, and forwards it unmodified to the app-supplied handler as the tenant identifier: [4](#0-3) 

The `WebhookMetadata` struct and the gem's own documentation instruct consuming apps to treat `data.shop` as "The shop domain of the webhook" and to key business logic off it directly: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `HMAC-verified bytes == bytes used to determine the tenant (shop)`. In this gem it instead holds `HMAC-verified bytes == raw_body only`, while `shop used by handler == unauthenticated header value`. Because the HMAC is computed with the app's own `api_secret_key`/`old_api_secret_key` over `raw_body` alone, and the shop header is not mixed into that computation anywhere: [7](#0-6) 

...a request satisfying `Registry.process`'s only check can carry a `shop`/`topic`/`webhook-id`/`api-version` combination that has never been signed by Shopify in association with that body.

### Impact Explanation
An unprivileged actor who can obtain one legitimately Shopify-signed webhook body+HMAC pair for *their own* shop (any developer can install their own app and receive real webhooks from Shopify, since HMAC secret is shared per-app not per-shop) can replay that exact `raw_body`/`hmac-sha256` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim merchant's domain. `HmacValidator.validate` still succeeds because only the body bytes are checked, and `Registry.process` dispatches to the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain. Any app logic that uses `data.shop` to select which merchant's records to update (exactly what the gem's own docs recommend, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will act on attacker-supplied webhook content while believing it originated from, and applies to, the victim tenant — a cross-tenant confusion/write primitive. This satisfies the "cross-tenant access" criterion for Critical impact, since the trust boundary between tenants collapses without any credential of the victim being required.

### Likelihood Explanation
Reaching this requires only a public HTTP endpoint (a normal, documented deployment configuration for `ShopifyAPI::Webhooks::Registry.process`) and one previously-observed valid `(raw_body, hmac)` pair for any shop under the same app (trivially obtainable by installing one's own store, or from any shop that already leaked one such pair, e.g. via logs). No access token, `client_secret`, or TLS interception is needed — the whole point of the flaw is that the shop identity is unauthenticated. This is a straightforward, low-effort replay once a single valid signed body is known.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is HMAC-verified, or otherwise cryptographically bind the header-derived `shop` to the signed body before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated header values and must not be used for authorization or tenant selection without additional verification (e.g., cross-checking against a known/registered shop for the webhook subscription, or validating against Shopify's IP ranges/registered callback per shop).

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com` and configure a webhook subscription (e.g., `orders/create`). Trigger the webhook so Shopify sends a legitimately signed POST to the app's callback endpoint; capture the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header value.
2. Re-issue the identical HTTP POST to the same app endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but replace `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. Server-side: `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` — [1](#0-0)  — and passes.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` — [8](#0-7)  — using the spoofed `victim.myshopify.com` value, and invokes the app's handler, which (per the gem's documented pattern) performs tenant-scoped work keyed on `data.shop`, now operating against the victim tenant with attacker-controlled body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
