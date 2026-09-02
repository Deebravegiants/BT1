### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values are read from unauthenticated HTTP headers that are never included in the signed material. `Registry.process` validates the HMAC and then trusts `request.shop` to attribute the webhook payload to a tenant, letting an attacker who controls the headers reassign a validly-signed webhook body to an arbitrary shop.

### Finding Description
`Utils::VerifiableQuery#to_signable_string` is the data that gets HMAC-verified by `Utils::HmacValidator.validate`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `Request#shop` (the tenant identity used downstream) is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed string: [3](#0-2) 

`Registry.process` validates the HMAC over the body and then, without any additional binding check, builds `WebhookMetadata` using this unverified `request.shop` value and dispatches it to the app's handler: [4](#0-3) 

This breaks the intended identity binding `hmac_verified_body == shop_that_sent_it`. The HMAC only proves "this body was signed with our `api_secret_key` at some point," not "this body came from shop X." Since `shop` is excluded from `to_signable_string`, any two requests with the same body and a valid HMAC will pass validation regardless of which `shop-domain` header is attached.

### Impact Explanation
An unprivileged internet user who is a legitimate merchant of the same app (i.e., they receive real webhooks with valid HMACs for their own shop) can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` still succeeds (it never looks at the header), so `Registry.process` calls the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop while the payload contents are the attacker's own. Any app that uses `WebhookMetadata#shop` — the field the gem itself exposes as the tenant identifier — to select which merchant's state/session/data to act on (e.g., "delete data for shop", "update order for shop", "revoke shop") will act cross-tenant, since the gem provides no mechanism to bind the actual sender shop to the verified payload. This is a cross-tenant confusion rooted entirely in this gem's webhook verification design, matching the Critical impact tier (cross-tenant access).

### Likelihood Explanation
Any merchant who has installed the app (a normal, unprivileged position — no `api_secret_key`, access token, or special access required) automatically receives valid `(body, hmac)` pairs from Shopify for their own shop and can trivially replay them with a forged `shop-domain` header to the app's public webhook endpoint. No secret material needs to be forged because the header is simply not covered by the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) inside the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the verified body before it's handed to `WebhookMetadata`/the handler. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header value so `HmacValidator.validate` fails when the header is altered relative to what was actually signed by Shopify for that delivery.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify delivers a real webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same `B`/`H` pair to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(secret, B) == H` — this still passes:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the attacker's own webhook body is now attributed to `victim-shop.myshopify.com` in the app's handler logic.

### Citations

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
