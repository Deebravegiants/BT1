This confirms the vulnerability. The `x-shopify-shop-domain` header (and `topic`, `webhook-id`, `api-version` headers) are **not covered by the HMAC signature** — the HMAC (`Request#to_signable_string`, `lib/shopify_api/webhooks/request.rb:35-38`) only signs `@raw_body`, while `Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`) reads the shop identity from an unsigned header. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates only the HMAC over the body and then trusts `request.shop` to build `WebhookMetadata`, which is the value host apps use to attribute the webhook payload to a tenant.

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the shop identity (`x-shopify-shop-domain`), topic, webhook id, and api version are all taken from unsigned HTTP headers. `Registry.process` validates the HMAC and then trusts these unsigned headers to construct the `WebhookMetadata` delivered to the host application's handler.

### Finding Description
The identity binding that should hold is: `shop used to attribute the webhook == shop over which the HMAC was computed`. In this gem that equality is broken:

- `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) calls `Request#to_signable_string`, which returns only `@raw_body` [1](#0-0) .
- `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers that are never included in the signable string [2](#0-1) .
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` (which verifies the body against the secret) before handing `request.shop`/`request.topic`/etc. straight into `WebhookMetadata` for the app's handler [3](#0-2) .

Because the shop domain is not part of what is HMAC-authenticated, any body+HMAC pair that was legitimately generated for one shop (e.g. from a webhook sent to the attacker's own store, or any store the attacker controls or observes) remains a **valid signature** even when replayed with a different `x-shopify-shop-domain` header. `OpenSSL.secure_compare` in `HmacValidator.validate_signature` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) will still pass because it only ever compares against the body bytes.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an attacker who can replay or forge the delivery envelope (headers are attacker controlled at the HTTP layer, only the raw body is checked) can make the app process webhook data while asserting it originates from an arbitrary shop domain, without ever needing the app's `client_secret`/`api_secret_key` beyond what is required to produce one valid body+HMAC pair for any store. This enables cross-tenant data injection/attribution — e.g., an `orders/create` or `app/uninstalled` webhook whose body happens to be reusable across shops can be replayed against another merchant's tenant context, since `WebhookMetadata#shop` is the value host apps key off of to select tenant data/session.

### Likelihood Explanation
Exploitability requires the attacker to obtain (or generate) one valid `(raw_body, hmac)` pair — trivially achievable if the attacker owns a development/trial store that receives real webhooks from Shopify, since Shopify signs with the same `api_secret_key` for every shop of the app. The attacker then only needs to change the `x-shopify-shop-domain` (and optionally `topic`/`webhook-id`) header when POSTing to the app's webhook endpoint, since this gem performs no binding of headers to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the value that gets HMAC-verified, or otherwise cryptographically bind them to the signed body, e.g. by having `Request#to_signable_string` incorporate the normalized header values, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`/`state`/`code` together (`lib/shopify_api/auth/oauth/auth_query.rb:33-43`). At minimum, document/enforce that host applications must not trust `WebhookMetadata#shop` unless verified against a caller-side registration.

### Proof of Concept
1. Register/own a development store `attacker.myshopify.com` for the app, and let Shopify deliver a real webhook (e.g. `orders/create`) — capture `raw_body` and the `X-Shopify-Hmac-Sha256` header.
2. Replay this exact HTTP request to the app's webhook endpoint, only replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in `Registry.process` succeeds because it validates only `@raw_body` against the secret [4](#0-3) .
4. `WebhookMetadata.shop` is now `"victim.myshopify.com"` [5](#0-4) , and the host app's handler processes/stores the attacker-controlled body under the victim's tenant.

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
