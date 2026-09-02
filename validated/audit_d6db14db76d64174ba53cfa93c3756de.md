## Title
Webhook `shop-domain` and `topic` headers are trusted for tenant/handler routing without HMAC coverage — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw JSON body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` uses the unverified `topic` header to select a handler and passes the unverified `shop` header straight into the handler as the tenant identifier. This breaks the intended binding: `HMAC(raw_body)` should authenticate the whole webhook event (including which shop it is for), but in this gem it only authenticates the body bytes.

### Finding Description
The `HmacValidator.validate` check in `lib/shopify_api/utils/hmac_validator.rb` verifies the signature by calling `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` then uses the unverified `topic` to select the handler and forwards the unverified `shop` to the handler as the authoritative tenant identity, after only checking that the (body-only) HMAC is valid: [3](#0-2) 

The equality that should hold is:
`shop_claimed_by_header == shop_the_HMAC_actually_authenticates`

Because the HMAC only covers `raw_body`, this equality is not enforced by the library — any header value can be substituted while the HMAC remains valid for that body.

### Impact Explanation
An unprivileged internet user who has legitimately installed the app on their own shop can capture one valid `(raw_body, hmac)` pair produced by Shopify for their own shop's webhook (this is nothing more than a webhook delivery to an endpoint they control), then replay that exact body+hmac to the app's webhook endpoint while altering the `shopify-shop-domain` and/or `shopify-topic` headers. `HmacValidator.validate` still passes because it only checks the body against the HMAC, and `Registry.process` will route the forged topic/shop into the corresponding handler. If the host application uses `WebhookMetadata#shop`/`#topic` to key per-tenant records (a documented, expected usage pattern shown in the gem's own docs), this allows cross-tenant data confusion — an attacker-controlled body can be attributed to a victim shop or a different (unregistered/mandatory) topic than the one Shopify actually sent.

This satisfies the cross-tenant-access class of impact: the gem provides no way for a consuming app to distinguish "the shop/topic that was actually signed" from "the shop/topic claimed in headers," because the former does not exist — only the body is signed.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that trusts `data.shop`/`data.topic` from `Registry.process` without independently cross-checking the target shop against a known session/store (which is exactly the pattern the gem's own docs/tests demonstrate). No secrets are required — only a single legitimately-delivered webhook payload from Shopify to the attacker's own installed shop, which any merchant/installer of the app can obtain.

### Recommendation
Bind the routing/tenant fields into the signed material, or verify them out-of-band before trusting them:
- Compute/verify the HMAC over a canonical string that includes `shop`, `topic`, and other routing headers in addition to the raw body, or
- Require callers of `Registry.process` to cross-check `request.shop` against the shop associated with the resolved session/store before invoking any handler, and document this requirement prominently, or
- At minimum, have `Registry.process` refuse to dispatch when the resolved `shop` cannot be corroborated against a known/authenticated tenant record.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com` and receive one legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B`).
2. Replay the exact same request to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com` and/or `x-shopify-topic` to another registered topic.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares it to `H` — it matches because the body `B` is unchanged. `hmac_validator.rb` line 190 check passes: [4](#0-3) 

4. The handler registered for the forged topic is invoked with `WebhookMetadata.new(topic: <forged topic>, shop: "victim.myshopify.com", body: <attacker's parsed body>, ...)`, and if the host app persists/acts on this data keyed by `shop`, it will act on data attributed to `victim.myshopify.com` even though Shopify never sent this event for that shop.

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
