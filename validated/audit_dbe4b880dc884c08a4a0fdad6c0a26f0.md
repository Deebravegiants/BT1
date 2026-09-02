### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross‑tenant shop spoofing on replayed webhooks - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then hands the handler a `WebhookMetadata` object built from HTTP headers — including `shop` — that are never included in the signed material.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`. For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, completely outside the HMAC's protected scope: [2](#0-1) 

`Registry.process` only checks the HMAC of the body and then forwards `request.shop` — the unauthenticated header value — directly into the tenant-identifying `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The binding that should hold is: `shop used for tenant attribution == shop cryptographically bound to the signed payload`. Instead, only `raw_body == HMAC(raw_body, secret)` is verified; the `shop-domain` header is disjoint from the signed bytes, so `shop` can be swapped freely as long as the body+HMAC pair itself remains valid for *some* installation of the app.

Because Shopify apps use a single shared `api_secret_key` for all shops (not a per-shop secret), any merchant who installs the app on their own store receives genuinely-signed webhook deliveries (valid body + HMAC) for their own shop. That merchant can capture one such delivery and replay the identical `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Registry.process` will accept it as fully valid (the HMAC check passes because the body wasn't modified) and dispatch it to the handler tagged with the victim's shop, since nothing in this gem verifies that the shop header corresponds to the shop the body was actually generated for.

### Impact Explanation
This crosses a tenant boundary: an unprivileged merchant (who legitimately controls only their own shop/webhooks) can cause the app to process attacker-supplied data under a victim shop's identity. Any app logic keyed off `WebhookMetadata#shop` (e.g., updating per-shop state, triggering per-shop side effects, writing to the victim's records) can be corrupted or manipulated cross-tenant — this matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker be a merchant capable of installing the target app on their own store and observing at least one webhook delivery — no access to the app's `api_secret_key`, access tokens, or privileged credentials is needed. The replay is a straightforward HTTP request with header substitution.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified signable string, or otherwise require the host application/`Registry.process` to cross-check the header-derived `shop` against a value that is independently authenticated per shop (e.g., verify against the shop associated with an existing stored session/registration for that webhook subscription) before constructing `WebhookMetadata`. At minimum, document and enforce that `shop` must not be trusted for tenant routing unless it is corroborated by data covered by the HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, granting the app's webhook subscription to fire for a topic (e.g. `orders/create`).
2. Shopify delivers a webhook with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared `api_secret_key`, and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures the raw body + HMAC header pair.
4. Attacker replays the exact same body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which passes because the body is unmodified; it then builds `WebhookMetadata.new(topic: ..., shop: request.shop, ...)` using the attacker-controlled `shop` header and invokes the handler, causing the app to process attacker data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
