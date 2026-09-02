This confirms the analog: the `shop` value delivered to the app's `WebhookHandler` is read directly from the unauthenticated `x-shopify-shop-domain` HTTP header, while the HMAC that `Registry.process` validates covers only the raw body bytes.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant shop-attribution spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value passed to app webhook handlers from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but `to_signable_string` — the data that `Utils::HmacValidator.validate` actually authenticates — is only the raw request body. The header is never included in the HMAC computation, so `Registry.process` accepts any shop-domain header value as long as the body+hmac pair is valid for *some* shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only, excluding all headers: [1](#0-0) 

`Webhooks::Request#shop` is populated purely from the caller-supplied header, with no cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then trusts `request.shop` when constructing the data passed to the app's registered handler: [3](#0-2) 

The equality that should hold but is broken is: *the shop the HMAC authenticates* (nothing — HMAC only covers `@raw_body`) ≠ *the shop the handler acts on* (`request.shop`, taken from an attacker-controllable header). An attacker who legitimately controls one Shopify store (their own trial/dev store) that has installed the app receives real, validly-signed webhook deliveries from Shopify for that store. Since the HMAC only signs the body, the attacker can replay that same valid `(raw_body, hmac)` pair to the app's public webhook endpoint while swapping the `shop-domain` header to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks body+secret), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the spoofed victim domain, as documented for consumers of this gem: `WebhookMetadata` exposes `shop` as the trusted tenant identifier for the handler. [4](#0-3) 

### Impact Explanation
Apps built on this gem are documented to use `data.shop` from `WebhookMetadata` directly to key per-tenant storage/lookups (as shown in the gem's own usage docs, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`). [5](#0-4) 
Since the gem itself hands the handler an attacker-controllable tenant identifier while only having verified the body's authenticity, any host application that follows the gem's own documented pattern is exposed to cross-tenant data confusion: mandatory-topic webhooks such as `customers/redact` or `shop/redact` could be attributed to the wrong shop, or ordinary topic webhooks (e.g., `orders/create`) could cause the app to write/attribute data belonging to the attacker's own shop under a victim's shop record. This crosses the tenant boundary this gem is responsible for establishing (shop identity for a webhook event), qualifying as cross-tenant access.

### Likelihood Explanation
Exploitation requires only an off-the-shelf Shopify development/trial store (freely obtainable by any unprivileged internet user) that installs the target app, and the ability to send arbitrary HTTP requests with custom headers to the app's public webhook endpoint (which is inherently internet-reachable for Shopify to reach it). No access to the app's `client_secret`, access tokens, or any privileged account is required — the attacker only needs a genuine `(raw_body, hmac)` pair for their own store, which Shopify will supply automatically upon any subscribed event.

### Recommendation
Bind the shop domain into the authenticated signable content, or otherwise verify that `shop` corresponds to the shop that legitimately owns the webhook subscription (e.g., cross-check against the webhook's registered `address`/expected shop context, or include the shop domain in the HMAC-covered string) before exposing it to `WebhookHandler` implementations. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be independently verified by the host app before being trusted as a tenant key.

### Proof of Concept
1. Attacker creates/uses a Shopify development store `attacker-shop.myshopify.com` and installs the target app, subscribing to a webhook topic (e.g., `orders/create`).
2. Shopify sends a legitimately signed webhook to the app's endpoint: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` with the app's `client_secret`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and replays it to the same endpoint, changing only the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`, keeping body `B` and `H` unchanged.
4. `Utils::HmacValidator.validate` in `Registry.process` recomputes the HMAC over `B` only and succeeds, since it never inspects the `shop-domain` header. [3](#0-2) 
5. The registered `WebhookHandler#handle` is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the event body actually originated from and describes `attacker-shop.myshopify.com`'s data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
