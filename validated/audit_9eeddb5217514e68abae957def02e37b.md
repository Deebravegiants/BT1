### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) fields are trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to identify *which merchant* the webhook is about are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` validates the HMAC and then hands these header-derived values straight to the app's handler as trusted tenant-identifying metadata, breaking the binding between "bytes verified by HMAC" and "bytes used to select the tenant/shop context."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight out of headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC (which covers the body), then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` that is delivered to the app's handler as the record of *which merchant* the webhook concerns: [3](#0-2) 

The equality the code implicitly assumes is:

`bytes verified by HMAC (raw_body)` == `bytes trusted for shop/tenant identification (shop-domain header)`

This equality does not hold: `secret = Context.api_secret_key`, `hmac = HMAC(secret, raw_body)`, but `shop` is never an input to `hmac`. Any unprivileged internet user who has ever received one genuine webhook delivery for *their own* installed shop (trivial to obtain — install the app on any dev/test store) possesses a valid `(raw_body, hmac)` pair signed with the app's real secret. That pair remains valid regardless of the `shop-domain` header value sent alongside it, because the header is not part of the signed content.

### Impact Explanation
An attacker can POST the captured, still-valid `(raw_body, hmac)` pair directly to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with a victim shop's domain. `Utils::HmacValidator.validate` will pass (it only checks the body-derived HMAC), and the app's registered handler will receive `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop — exactly the "shop" field the library itself hands to app code as authenticated tenant context. Depending on how the host app keys its per-shop data/state on this field (which is the documented and only field provided by this gem for that purpose, see `test/webhooks/registry_test.rb` assertions on `data.shop`), this enables cross-tenant data corruption/injection: attacker-chosen payloads get attributed to, and processed under, a shop the attacker does not control.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining one legitimate `(raw_body, hmac)` pair only requires installing the app on any shop the attacker controls (no special privilege, no leaked secret, no TLS interception). Replaying it with a forged `shop-domain` header against the public webhook endpoint is a single unauthenticated HTTP request.

### Recommendation
Bind the tenant-identifying fields to the signature rather than trusting raw headers: either include `shop`, `topic`, and `webhook_id` in the HMAC-signed payload (requires coordinated change with Shopify's webhook signing scheme), or, at minimum, have `Registry.process`/consuming apps cross-check `request.shop` against the shop associated with the currently active/stored session for the delivery before acting on it, so a header value alone can never redirect processing to an unintended tenant.

### Proof of Concept
1. Attacker installs the target app on their own test shop `attacker-shop.myshopify.com`, triggering a real webhook delivery with a valid HMAC computed by Shopify using the app's real `client_secret`.
2. Attacker captures the raw body and the `x-shopify-hmac-sha256` value from that delivery.
3. Attacker sends a raw HTTP POST directly to the app's public webhook endpoint with:
   - the same captured `raw_body` and `hmac` header (still valid, since `Request#to_signable_string` only signs the body — [4](#0-3) )
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate(request)` returns `true` (body HMAC matches), so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` — [3](#0-2) , letting the attacker's payload be processed under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
