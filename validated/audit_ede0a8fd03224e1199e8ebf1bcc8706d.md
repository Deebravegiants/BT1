## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates an incoming webhook solely with `Utils::HmacValidator.validate(request)`, which only authenticates the raw request body. The `shop-domain` header that the handler receives as the tenant identifier is never part of the signed material, so it can be freely substituted by anyone who can produce one valid, HMAC-signed webhook for the shared app secret (i.e., any shop that has installed the app).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the HMAC exclusively over that signable string and compares it against the `hmac-sha256` header: [2](#0-1) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated headers: [3](#0-2) 

`Registry.process` only checks the HMAC and then hands `request.shop` straight to the app's handler as the tenant identity, with no additional binding between the signed body and the claimed shop: [4](#0-3) 

The equality this implicitly assumes is:
`hmac_valid(body) == shop_header_is_authentic`

but the actual binding enforced by the code is only:
`hmac_valid(body) == body_was_signed_by_api_secret_key`

Because a single `api_secret_key` is shared by the app across every shop that has installed it, any shop (a legitimate but lower-privileged tenant relative to other merchants of the same app) can capture one of its own genuine webhook deliveries (raw body + valid `hmac-sha256`) and replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. `Registry.process` (and thus `Utils::HmacValidator.validate`) will accept it as valid, since the shop header plays no part in the signature, and the handler will process the (attacker-controlled, but validly-signed-in-isolation) payload as if it belonged to the victim shop identified by the spoofed header.

### Impact Explanation
This breaks the tenant/shop identity binding that webhook consumers rely on (`WebhookMetadata#shop` is passed to the handler unauthenticated), enabling cross-tenant data confusion/injection: an app that keys any state, side effects, or authorization decisions off `data.shop` from `Registry.process` can be made to act on a forged tenant identity using otherwise-legitimate signed traffic from a different, lower-trust tenant. This matches the "cross-tenant access" category.

### Likelihood Explanation
Any shop that has installed the app (a normal, unprivileged merchant relative to other tenants) already receives real webhooks signed with the app's single shared `api_secret_key`, so obtaining one valid body+HMAC pair requires no special access beyond normal app usage — no leaked secrets or elevated privileges are required to mount the cross-tenant spoof against the shop-domain field.

### Recommendation
Bind the `shop-domain` (and ideally `topic`, `api_version`, `webhook_id`) into the signed material that is verified, or require the caller (host application) to separately verify that `shop` matches an install actually authorized for the received body/topic. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification (e.g., cross-checking against a known, previously stored session for that shop before trusting webhook content).

### Proof of Concept
1. App is installed on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com`, sharing one `api_secret_key`.
2. From `attacker-shop.myshopify.com`, capture a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-SHA256: H` (valid HMAC of `B` under the shared secret).
3. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`.
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, processing attacker-controlled content as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
