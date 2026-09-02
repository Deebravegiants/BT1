### Title
Webhook shop identity not covered by HMAC signature allows cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, while the HMAC signature verified by `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body. Because the shop header is not part of the signed material, an attacker who can obtain one genuine, validly-signed webhook (e.g., by installing the target app on their own shop) can replay that exact body/HMAC pair while substituting an arbitrary `shop` header value. The gem's HMAC check still passes (it only re-hashes the body), and the handler is invoked believing the webhook belongs to a different, victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` field using `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body — the `shop` (and `topic`, `webhook_id`, `api_version`) values come from headers and are never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The binding this breaks is:
`shop_used_by_handler(request.shop) == shop_that_actually_produced_and_signed(raw_body)`

Before the attacker's action, this equality holds for genuine Shopify-forwarded requests. After the attacker's action — capturing a real webhook delivered to their own shop (any unprivileged internet user can install any public app and receive its webhooks) and re-POSTing the identical `raw_body`/`hmac-sha256` pair to the app's webhook endpoint with a forged `shopify-shop-domain` header naming a victim shop — `Utils::HmacValidator.validate` still returns `true` because the body is byte-identical and the HMAC only covers the body, but `request.shop` now names an unrelated tenant. `Registry.process` proceeds to invoke the handler with `WebhookMetadata.new(... shop: request.shop ...)`, so the app processes attacker-controlled body content under a victim shop's identity.

### Impact Explanation
This is a cross-tenant identity-binding bypass entirely within the gem's own webhook verification path: the gem asserts that a webhook "belongs" to a shop based on an unauthenticated header while advertising a "validated" HMAC that does not cover that field. Any host application that relies on `WebhookMetadata#shop` (as the gem's own webhook docs and its `Request`/`Registry` API instruct) to scope data writes, cache keys, or session lookups per tenant can be made to apply attacker-supplied webhook payload data to a different merchant's tenant context, without ever possessing that merchant's credentials or the app's `client_secret`.

### Likelihood Explanation
The only prerequisite is the capability of any unprivileged internet user: installing the target app on a shop they control (development store or trial), capturing one legitimate webhook delivery, and replaying it with a modified header — no `api_secret_key`, access token, or privileged account is required. This is straightforward to automate and repeat for any topic/body content the attacker's own shop can trigger.

### Recommendation
Include the shop domain (and other identity-bearing headers such as `webhook_id`/`topic`) in the HMAC-verified signable material, or otherwise cryptographically bind the shop identity to the signed payload (e.g., re-deriving/validating the shop from a value inside the signed body, or requiring the host app to cross-check the header shop against a shop already known/authorized for that webhook subscription) before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`) that the app has subscribed to via webhooks.
2. Shopify delivers the webhook to the app's public HTTPS webhook endpoint with headers:
   - `shopify-hmac-sha256: <valid HMAC of raw body, using app's real secret>`
   - `shopify-shop-domain: attacker-shop.myshopify.com`
   - raw body `B`
3. Attacker captures this full HTTP request (both are visible to them as the shop owner).
4. Attacker re-sends the same request to the same endpoint, keeping `raw_body = B` and `shopify-hmac-sha256` unchanged, but replacing `shopify-shop-domain` with `victim-shop.myshopify.com`.
5. In the gem: `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)` is built; `hmac` still decodes to the same valid signature; `Utils::HmacValidator.validate(request)` recomputes the HMAC over `B` only and returns `true`. [4](#0-3) 
6. `Registry.process` invokes the handler with `shop: request.shop` = `"victim-shop.myshopify.com"`, even though the payload `B` originated from the attacker's own shop's event, achieving cross-tenant confusion in the host application.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
