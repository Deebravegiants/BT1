### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then unconditionally trusts the `shop` (and `topic`/`webhook_id`) values taken from HTTP headers to build the `WebhookMetadata` that is handed to the app's handler. Because the shop identity is never part of the signed material, anyone who can produce one valid `(body, hmac)` pair for the shared app secret can replay it with an arbitrary `x-shopify-shop-domain` header and have it accepted as originating from a different merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `shop` is read straight from an unauthenticated header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header — it never incorporates `shop`, `topic`, `api_version`, or `webhook_id`: [3](#0-2) 

`Registry.process` then trusts `request.shop` unconditionally once the body HMAC passes, and forwards it as the tenant identifier to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is the field host apps use to bind webhook data to a specific merchant/session, as documented and shown in the gem's own usage guide (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [5](#0-4) 

The identity binding that should hold is: `shop_bound_by_signature == shop_used_by_handler`. Because the HMAC secret (`Context.api_secret_key`) is the app's single client secret shared across **every** shop that installs the app — not a per-shop secret — any merchant who has installed the app receives genuine webhooks for their own store containing a valid `(raw_body, hmac)` pair computed with that shared secret. That merchant can capture one such legitimate webhook and replay it directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a different, victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` dispatches the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain — a cross-tenant identity forgery entirely within this gem's own verification logic.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an unprivileged merchant on a multi-tenant app can make the app believe arbitrary webhook events (including sensitive topics such as `app/uninstalled`, `orders/create`, `customers/data_request`, etc.) originated from a shop they do not control. Depending on how the host app trusts `data.shop` (which the gem explicitly recommends using as the tenant key, e.g. for job dispatch), this can lead to cross-tenant data corruption, false uninstall/GDPR events being processed for a victim shop, or injection of forged order/customer data attributed to another merchant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any shop that installs the vulnerable app is, by definition, capable of receiving legitimately signed webhooks for itself, and the app secret is shared across all installations of that app. Capturing one's own legitimate webhook body+HMAC and replaying it against the app's public webhook endpoint with a modified shop header requires no special privilege beyond installing the app — an ordinary unprivileged capability for a multi-tenant SaaS app.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable material, or otherwise cryptographically bind `request.shop` to the verified body (e.g., derive/verify shop identity from a value that is itself part of the signed payload, or maintain a per-shop secret/lookup and validate the header against the shop record associated with the webhook subscription) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on `victim-shop.myshopify.com`, both under the same app (shared `api_secret_key`).
2. Shopify sends a legitimate webhook to the app's endpoint for `attacker-shop.myshopify.com`:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body with app secret>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   body: {...}
   ```
3. Attacker replays the exact same body and HMAC header to the app's endpoint, only changing:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) passes because it only checks `body` against `hmac`.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` and invokes the app's handler as if the event genuinely came from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
