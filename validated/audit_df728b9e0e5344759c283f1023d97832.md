### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by checking the HMAC of the raw request body, but then hands the caller's `shop`, `topic`, `webhook_id`, and `api_version` HTTP headers — none of which are covered by that HMAC — straight to the app's `WebhookHandler`. This is the same identity-binding class of bug as the reported Autonomint issue: a value that is *acted upon* (here, the tenant/shop identity attached to webhook data) is not the value that was actually *verified* (only the JSON body bytes are verified).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates only this body HMAC via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`WebhookMetadata` carries `shop` as a plain, unauthenticated `String` field consumed by the handler to decide which tenant the payload belongs to: [4](#0-3) 

This contrasts with the OAuth callback path in the same library, where the analogous `shop` field *is* included in the signed string (`AuthQuery#to_signable_string` includes `shop`), showing the gem is capable of, but does not apply, the same protection to webhooks: [5](#0-4) 

**Broken equality (identity binding):** the library implicitly assumes
`bytes_verified_by_hmac (raw_body) == identity_acted_upon (shop header used for tenant routing)`
but in fact only `raw_body` is verified while `shop`/`topic`/`webhook_id` headers are parsed and trusted unverified, i.e. `bytes_verified != identity_used`.

### Impact Explanation
Any unprivileged party who can install the app on their own store (an ordinary merchant account, not requiring `api_secret_key`, an access token, or any privileged Shopify role) will legitimately receive real webhook deliveries for their own shop — each with a valid `hmac-sha256` for a given `raw_body`. Because the HMAC never covers the `shopify-shop-domain` (or `shopify-topic`/`shopify-webhook-id`) header, that attacker can replay the exact same body + HMAC pair to the target app's webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Utils::HmacValidator.validate` still succeeds (the body bytes are unchanged), and `Registry.process` dispatches the handler with `shop: <victim-shop>`, causing the host application to process attacker-controlled payload content as if it originated from — and applies to — a different tenant. This crosses the tenant boundary the webhook subsystem is meant to enforce, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no secrets: an attacker only needs their own (even a free/trial) shop with the app installed to obtain a genuine `(raw_body, hmac)` pair, then a way to POST an HTTP request with modified headers to the app's public webhook endpoint. Both preconditions are attacker-controlled and require no elevated privilege, making the attack straightforward for a motivated unprivileged party once they understand which headers are unauthenticated.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or otherwise cryptographically bind the routing metadata) in the value verified by `Utils::HmacValidator`, or, at minimum, require the host application to cross-check `request.shop` against a known/expected shop for the session/tenant before invoking the handler. Alternatively, document explicitly (and ideally enforce in `Registry.process`) that `shop`/`topic`/`webhook_id` are unauthenticated and must be independently validated by the consuming application before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an event (e.g., updates a product) to receive a legitimate webhook delivery with body `B` and header `shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `client_secret`).
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body successfully (`lib/shopify_api/webhooks/request.rb:45-63`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) and succeeds because `B` and `H` are unmodified (`lib/shopify_api/webhooks/registry.rb:188-190`).
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)` and processes attacker-supplied data attributed to the victim tenant.

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
