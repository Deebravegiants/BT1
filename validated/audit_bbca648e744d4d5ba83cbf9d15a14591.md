### Title
Webhook shop/topic identity spoofing via unauthenticated headers outside the HMAC-signed byte range - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers, but `to_signable_string` — the data that `HmacValidator` actually verifies — is only the raw request body. Any caller who can produce one valid `(body, hmac)` pair signed with the app's shared `client_secret` (e.g. an attacker who installs the app on their own shop and receives a legitimate webhook) can replay that exact body/HMAC pair while freely rewriting the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers, and `Registry.process` will still treat the request as authentic and dispatch it to the handler tagged with the attacker-chosen tenant identity.

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all parsed from HTTP headers that are never included in the signed bytes: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then trusts `request.shop` (and `request.topic`) unconditionally to build `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `bytes_verified_by_hmac == bytes_used_to_derive_shop/topic`. Here, `bytes_verified_by_hmac = raw_body` while `bytes_used_to_derive_shop = shopify-shop-domain header`, which is disjoint from the verified byte range. Since Shopify apps share a single `client_secret` across every merchant that installs the app, an unprivileged attacker can:
1. Install the app on their own (attacker-controlled) shop, and capture one legitimate webhook delivery — a `(raw_body, X-Shopify-Hmac-Sha256)` pair that is valid because it was signed by Shopify with the app's `client_secret`.
2. Replay that identical body+HMAC to the app's webhook endpoint, but swap the `X-Shopify-Shop-Domain` header to a victim shop's domain (and optionally the topic/webhook-id/api-version headers).
3. `HmacValidator.validate` still returns `true` because it only checks the untouched raw body, so `Registry.process` accepts the forged request and calls the app's handler with `WebhookMetadata#shop` set to the victim's domain.

The documented usage pattern in this gem explicitly assumes `data.shop` is a trustworthy per-tenant identifier that host apps use to route processing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so this misbinding directly propagates a forged tenant identity into the host application's business logic.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (but unprivileged) merchant/installer of the app can forge webhook payloads that are accepted as coming from a different shop, without ever needing that shop's credentials, access token, or the app's `client_secret`. Depending on how the host application implements its handler (which the gem's own documentation encourages — keying background jobs or state updates by `data.shop`), this enables cross-tenant data corruption/injection: attacker-controlled webhook body content gets attributed and processed under a victim shop's identity. This matches the Critical "cross-tenant access" impact category in scope.

### Likelihood Explanation
Medium-to-high. It requires the attacker to be a real, unprivileged installer of the target app (trivial for public/embeddable apps, since anyone can install a Shopify app on their own dev/test store) and to control raw HTTP headers to the app's own publicly reachable webhook endpoint (trivial — no Shopify infrastructure needs to be bypassed, the request goes straight to the app server). No secrets beyond what the attacker legitimately receives (their own valid webhook deliveries) are required. The only constraint is that the forged request must reuse a body the attacker actually received a valid HMAC for; the header fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) can be freely modified as they are not covered by the signature.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable material for webhook requests, or otherwise cryptographically bind them to the body (e.g. concatenate them into the signed string, mirroring how `AuthQuery#to_signable_string` binds `code`, `host`, `shop`, `state`, `timestamp` for OAuth callbacks). At minimum, document prominently that `Webhooks::Request#shop`/`#topic`/etc. are unauthenticated and must not be trusted for tenant routing without additional verification (e.g. cross-checking against a known/stored shop record) by the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, since Shopify signs `B` with the app's shared `client_secret`), plus original header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the identical body `B` and header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally alters `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. Server calls `ShopifyAPI::Webhooks::Registry.process(request)`, which calls `Utils::HmacValidator.validate(request)`. Since `to_signable_string` returns only `B`, the HMAC check passes.
4. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))` executes with the attacker's chosen body content attributed to `victim-shop.myshopify.com`, exactly as shown in the gem's own documented handler pattern (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`). [5](#0-4)

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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
```
