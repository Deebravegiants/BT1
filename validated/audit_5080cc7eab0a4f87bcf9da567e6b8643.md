Confirmed root cause: `Registry.process` validates the webhook HMAC over the raw body only, then dispatches `request.shop` (taken from the `X-Shopify-Shop-Domain` HTTP header) to the handler as the tenant identifier — without that header ever being covered by the HMAC signature. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop attribution is derived from an unauthenticated HTTP header, not the HMAC-signed payload - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity via `Utils::HmacValidator.validate(request)`, which signs only `request.to_signable_string` (the raw request body). The `shop` value that the handler receives and uses to attribute the webhook event to a tenant is read directly from the `X-Shopify-Shop-Domain` header, which is never included in the HMAC-signed bytes.

### Finding Description
The equality that should hold is: `shop bound by HMAC == shop used to attribute the webhook event`. In this gem:
- `Request#hmac` reads `shopify-hmac-sha256` header and `Request#to_signable_string` returns only `@raw_body` [4](#0-3) [2](#0-1) .
- `Request#shop` is populated purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the body or the HMAC [5](#0-4) [6](#0-5) .
- `Registry.process` validates only the HMAC (which covers the body, not the shop header) and then hands `request.shop` straight to the host app's handler as the tenant identifier for the event [7](#0-6) .

This is precisely the analog class from the report: a field (`shop`) is acted on by the library but not covered by the HMAC that is supposed to authenticate the whole message. An attacker who has captured (or replays) one legitimate, validly-HMAC'd webhook body for their own shop can resend that exact request while altering only the `X-Shopify-Shop-Domain` header. Because the signature check only covers the raw body, the signature still validates, and the gem passes the attacker-chosen `shop` value into `WebhookMetadata#shop` used by the host app's handler [8](#0-7) .

Note: whether this results in real cross-tenant impact depends on the host application's handler logic (e.g., if it uses `data.shop` to decide which merchant record to update/delete without any secondary check). This gem provides the mistrustable field as authenticated-looking data, but the actual exploit requires the host app to trust `WebhookMetadata#shop` — this is an important caveat, since the analog rules exclude issues that depend solely on the host app ignoring documented API. Here, however, the gem itself presents `shop` as verified data via `Registry.process` after HMAC validation, without documenting that the shop field is unauthenticated, which is the root cause inside this gem's own code.

### Impact Explanation
If a host application relies on the gem's webhook `shop` field (as returned after passing `HmacValidator.validate`) to route data to the correct tenant, an attacker who can capture one valid signed webhook payload (e.g., from their own store, or a publicly observable webhook) can replay it with a forged shop-domain header and have the gem treat it as validated for a different tenant. This can result in cross-tenant data confusion/injection (e.g., triggering `customers/redact`, order updates, or app-uninstalled handling) attributed to a victim shop the attacker does not control — a cross-tenant impact.

### Likelihood Explanation
Exploitability requires the attacker to obtain at least one legitimately HMAC-signed webhook body (achievable by installing the app on their own store, which any developer/attacker can do), and requires the host app to trust the returned `shop` value without an independent check (e.g., without cross-referencing the registered callback URL or an app-specific per-shop secret). This is a plausible integration pattern given the gem's documented `WebhookMetadata` API returns `shop` as if it were verified.

### Recommendation
- **Short term:** Document explicitly that `WebhookMetadata#shop` is derived from an HTTP header not covered by the HMAC, and that host apps must independently verify the shop domain (e.g., against known installed shops/session store) before trusting it.
- **Long term:** Extend `VerifiableQuery`/`HmacValidator` usage for webhooks so that the shop domain (and other headers used for routing) are cryptographically bound to the signed payload, or have `Registry.process` cross-check `request.shop` against records tied to the delivery (e.g., the registered webhook's expected shop) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on their own development store `attacker.myshopify.com` and registers a webhook.
2. Shopify sends a legitimately signed webhook, e.g.:
   ```
   X-Shopify-Hmac-Sha256: <valid HMAC over body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Topic: customers/redact
   Body: {"customer": {...}}
   ```
3. Attacker replays this exact body and HMAC header to the app's webhook endpoint, but rewrites the header to:
   ```
   X-Shopify-Shop-Domain: victim.myshopify.com
   ```
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — passes, because the body/HMAC pair is untouched [9](#0-8) .
5. The gem builds `WebhookMetadata.new(..., shop: request.shop, ...)` with `shop = "victim.myshopify.com"` and calls the host's `handler.handle(data:)` [10](#0-9) .
6. Any host logic that trusts `data.shop` for tenant-scoped actions now operates against `victim.myshopify.com` using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
