## Finding

### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates its HMAC over the raw request body only, while the tenant-identifying `shop` (and topic/webhook-id) values come from unauthenticated HTTP headers that are never included in the signed content. Any party in possession of one validly-signed webhook delivery (e.g., from a shop they themselves control, since the app's webhook HMAC secret is the single `Context.api_secret_key` shared across every installation of the app) can replay that body/HMAC pair while swapping the `shop-domain` header to any other shop, and `ShopifyAPI::Webhooks::Registry.process` will accept it as valid and hand the attacker-controlled body to the app's handler tagged with the victim's shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from (attacker-controllable, at the transport layer) HTTP headers, independent of the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the HMAC header, and never binds `shop`/`topic`/`webhook_id` into that computation: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identity once the body HMAC passes, and forwards it straight to the app's handler: [4](#0-3) 

The equality this breaks is: `shop asserted by the HMAC-covered bytes` **should equal** `shop delivered to the handler as WebhookMetadata#shop`, but in fact the HMAC covers zero bytes of the shop identity — only `@raw_body` is signed. Since `Context.api_secret_key` is a single, app-wide secret (not per-shop), any tenant that has installed the app can legitimately trigger Shopify to send them a validly-HMAC'd webhook (e.g., by creating an order in their own store to trigger `orders/create`). They can then capture that `(raw_body, hmac-sha256 header)` pair and replay it to the app's public webhook endpoint with a forged `shop-domain` (and optionally `topic`/`webhook-id`) header pointing at a different shop that also uses the app. The signature still validates because the shop header was never part of the signed material, so `Registry.process` will invoke the topic handler with `WebhookMetadata#shop` set to the victim's domain and `body` fully attacker-controlled (subject to whatever body shape they can produce via their own store's events).

### Impact Explanation
This breaks the tenant boundary of the webhook processing pipeline: it allows one merchant/tenant to inject attacker-influenced data into another tenant's webhook processing path by forging the `shop-domain` header, since the value is never cryptographically bound to the payload. This meets the "cross-tenant access" Critical bar — the app's webhook handler will process data purportedly originating from a shop the attacker doesn't control and doesn't have credentials for.

### Likelihood Explanation
Exploitation requires only that the attacker (1) has the app installed on any shop (a normal, unprivileged merchant), which lets them obtain a validly signed webhook via ordinary store activity, and (2) can send an HTTP POST to the app's public webhook endpoint with modified headers — both are within reach of any unprivileged internet-connected merchant using the app, with no access to `api_secret_key` or any victim credentials required.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material used for HMAC validation, or otherwise cryptographically tie the header-derived `shop` to the verified payload (for example, by having `to_signable_string` incorporate the normalized headers, or by requiring the host application to cross-check `request.shop` against session/tenant records established independently of this header before trusting it).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers an `orders/create` event (e.g., places an order), causing Shopify to POST a validly HMAC-signed webhook to the app's registered endpoint:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - Body: `{...order json...}`
2. Attacker captures this exact `(body, hmac header)` pair (e.g., via their own reverse proxy/logging in front of their receiving endpoint, which they fully control since it's their own tenant's traffic).
3. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` and `to_signable_string` are unaffected by the header change (only `@raw_body` is signed), so `Utils::HmacValidator.validate` returns `true`.
5. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `WebhookMetadata#shop == "victim.myshopify.com"` and the attacker's body, even though `victim.myshopify.com` never sent this data.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
