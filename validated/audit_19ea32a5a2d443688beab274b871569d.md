Confirmed root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) signs only `@raw_body`, while `shop` (`x-shopify-shop-domain`/`shopify-shop-domain` header, line 21-23), `topic`, `api_version`, and `webhook_id` are all read from unauthenticated headers and passed straight into `WebhookMetadata` by `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) without any binding to the HMAC.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is verified against `to_signable_string`, which returns only the raw request body [1](#0-0) . The `shop` (`shopify-shop-domain`), `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers [2](#0-1)  and are never included in the HMAC-signed string, so `ShopifyAPI::Utils::HmacValidator.validate` only proves that *some* raw body was produced by an entity holding `api_secret_key` — it proves nothing about which shop the request headers claim to be from. `ShopifyAPI::Webhooks::Registry.process` trusts these unauthenticated headers and forwards `request.shop` directly into `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Finding Description
The identity binding broken here is: `shop claimed in header` == `shop that owns the HMAC-signed body`. Because the HMAC only covers `@raw_body`, an attacker who possesses one legitimate (body, HMAC) pair — trivially obtainable by installing the app on their own free/dev store and capturing a webhook Shopify sends them, since the raw body and HMAC are visible to the receiving endpoint's own attacker-controlled account — can replay that exact body+HMAC pair to the app's public webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop's domain. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) will still return `true`, because it only recomputes the HMAC over `@raw_body`, which is unchanged. `Registry.process` then builds `WebhookMetadata` with `shop: request.shop` set to the attacker-chosen victim domain, and the handler is invoked believing this is authentic data for the victim shop.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem cannot cryptographically trust `data.shop` in its `WebhookHandler#handle` implementation, even though the documented contract states `shop` is "The shop domain of the webhook" [4](#0-3) . Any app that uses `data.shop` to look up which shop's session/tokens to act on, or to attribute/store data (the documented usage pattern, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4) ) is exposed to cross-tenant data confusion: an attacker's own shop's webhook payload gets attributed to a victim shop of the attacker's choosing. This satisfies the "cross-tenant access" Critical impact criterion, since the gem itself fails to bind the two together despite HMAC validation succeeding.

### Likelihood Explanation
Likelihood is moderate-to-high: the attacker only needs an unprivileged Shopify partner/development store (free to create) to legitimately trigger and capture one webhook (body + valid HMAC) for a topic the target app registers, then replay it with a forged `shop-domain` header at the app's public webhook endpoint. No access to `api_secret_key`, no victim credentials, and no privileged account are required — only capturing traffic the attacker's own store legitimately receives.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material, or otherwise validate it out-of-band: at minimum, `ShopifyAPI::Webhooks::Request#to_signable_string` should not be the sole trust anchor for `shop` — the gem should document/enforce that consuming apps must independently verify `request.shop` corresponds to a shop that actually has this webhook topic registered/installed (e.g., cross-check against a known session store) before trusting `data.shop`, or the HMAC computation should incorporate the shop-identifying header so a body/HMAC pair cannot be replayed under a different shop identity.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify sends the attacker a legitimate webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same request to the app's public webhook endpoint, but rewrites `x-shopify-shop-domain` to `victim.myshopify.com` (or `shopify-shop-domain` in the new header format).
4. `ShopifyAPI::Webhooks::Request#hmac` decodes `H` unchanged; `to_signable_string` returns body `B` unchanged; `Utils::HmacValidator.validate` recomputes HMAC over `B` and it matches `H` → validation succeeds.
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: <parsed B>, ...)` and invokes the app's handler, which processes attacker-controlled/attacker-owned data as if it belongs to `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L19-29)
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
