### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` identity that is handed to the host application's webhook handler is read from an unsigned HTTP header. This breaks the intended binding `hmac_verified_bytes == identity_attributed_bytes`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` value that is later trusted and forwarded to the app's handler is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the signed body: [2](#0-1) .

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` and, once that check passes, immediately constructs `WebhookMetadata` using `request.shop` (the unsigned header) as the tenant identity that is delivered to the application: [3](#0-2) . `HmacValidator.validate_signature` computes `OpenSSL::HMAC.hexdigest` only over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the received signature: [4](#0-3) .

Because the HMAC only signs the body, the `(topic, shop, api_version, webhook_id)` headers are entirely excludable from the authenticity check. `WebhookMetadata` — the struct handed to the app's `WebhookHandler#handle` — nonetheless carries `shop` as an authenticated field: [5](#0-4) . This is precisely the "field acted on but not covered by the HMAC" analog: the equality that should hold — `hmac_signed(shop) == shop_used_by_handler` — does not hold, since `shop` is never part of the signed material at all.

**Exploitation path:** any actor who can obtain one legitimately-HMAC-signed payload+body pair for *any* shop (trivial: they simply run their own free/dev store, install the merchant's app, and trigger a webhook, e.g. `app/uninstalled` or `orders/create` with an attacker-controlled body) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming a victim shop. `HmacValidator.validate` still passes (it never looked at the header), and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the victim's domain and attacker-chosen `body`. Any host application that uses `data.shop` from this gem's webhook processing to key its per-tenant data store (which is the gem's own documented pattern, since `shop` is the struct's contractual identity field) will write/act on attacker-supplied data under a victim tenant's identity — a cross-tenant write, e.g. forging `app/uninstalled` to make the app tear down a victim's install, or forging order/customer data into the victim's tenant record.

### Impact Explanation
This meets the Critical bar: cross-tenant access. A network-only, unprivileged actor with no access token, no `client_secret`, and no privileged account can make a host application built on this gem attribute forged webhook bodies to any shop domain string, because this gem's `Registry.process`/`Request` never binds `shop` to the HMAC it validates.

### Likelihood Explanation
The attacker only needs the ability to (a) obtain any one valid signed webhook (trivially available by installing a free trial/dev store of the target app, which self-generates authentic webhook deliveries under the attacker's own shop), and (b) send an HTTP POST to the app's public webhook endpoint with a spoofed `shopify-shop-domain` header — no secrets, tokens, or privileged access required. This is a moderate-to-high likelihood scenario given webhook endpoints are public by design.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind `shop` to the body before trusting it (e.g., only accept `shop` values obtainable from Shopify's own signed body payload rather than an independent header), so that `Utils::HmacValidator.validate` fails whenever any of these fields have been altered.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook: body `{"id":1}` with header `x-shopify-hmac-sha256: <valid HMAC of body under app's secret>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body and HMAC to the app's public webhook endpoint but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (the unchanged body) and succeeds, since `request.shop`/header is never included: [3](#0-2) .
4. The app's `WebhookHandler#handle` receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` and performs tenant-scoped actions (e.g., data deletion/creation) against `victim-shop.myshopify.com` using attacker-controlled `body`, even though the request never actually originated from Shopify on behalf of that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
