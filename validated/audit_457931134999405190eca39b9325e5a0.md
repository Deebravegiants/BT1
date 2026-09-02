### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its `to_signable_string` from the raw HTTP body only, while `shop`, `topic`, and `webhook_id` are read directly from HTTP headers that are never included in the HMAC-verified content. `Registry.process` verifies the HMAC and then trusts these header-derived fields to route the payload to a tenant/handler, breaking the intended binding "the shop the HMAC authenticates" == "the shop the handler acts on."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`shop`, `topic`, and `webhook_id` are pulled straight from headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) and are not part of what `HmacValidator` verifies: [3](#0-2) 

`Registry.process` validates the HMAC and, if it succeeds, unconditionally trusts `request.topic` and passes `request.shop` straight into the handler's `WebhookMetadata`: [4](#0-3) 

Because only the raw body bytes are HMAC-verified, the identity binding the gem should guarantee — "HMAC(body, client_secret) is valid" implies "this body genuinely originates from `shop`" — does not hold. The gem lets a caller present the same verified body with an arbitrary `shopify-shop-domain` header and still pass validation, since `HmacValidator.validate` never inspects `shop`.

### Impact Explanation
This breaks the tenant-authentication boundary the gem is supposed to provide for webhook processing: `bytes verified (raw body)` != `bytes/identity acted on (shop header)`. Any user capable of triggering delivery of a legitimately-signed webhook for their own store (which any merchant/installer of the app can do, since it's their own shop's webhook, signed with the app's shared `client_secret` for all shops) can replay that same signed body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header for a victim shop. `Registry.process` will accept it as valid (HMAC passes because the body is untouched) and hand the handler a `WebhookMetadata` claiming the data came from the victim shop, causing the host application to process/attribute attacker-controlled data as belonging to a different tenant. This constitutes cross-tenant data injection/confusion within the gem's own webhook-processing contract.

### Likelihood Explanation
Likelihood is limited by the fact that an attacker needs a validly-signed body/HMAC pair, which they can trivially obtain by installing the app on their own store (a normal, unprivileged action any Shopify merchant can perform) and capturing one of their own real webhook deliveries. From there, forging the `shop-domain` header on a replayed request to the app's public webhook endpoint requires no secrets. Exploitability depends on the host app relying on `WebhookMetadata#shop` for tenant scoping without independent cross-checks, which is the documented/expected usage pattern of this API.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable content (or otherwise cryptographically bind them to the body, e.g., by validating them against a previously-established relationship for that shop) so that `HmacValidator.validate` cannot succeed unless the claimed shop/topic/id are exactly what Shopify actually signed. At minimum, document that `request.shop` must not be trusted without an out-of-band merchant/session validation, or reject requests where the signed body cannot be tied to the claimed shop.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; capture a genuine webhook Shopify sends to the app (raw body `B`, valid `shopify-hmac-sha256` header `H` — both signed with the app's shared `client_secret`).
2. Replay a POST to the app's webhook endpoint with the same body `B` and hmac header `H`, but change `shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(B, client_secret) == H`, which is unaffected by the header change.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-supplied data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
