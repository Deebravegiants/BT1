### Title
Webhook `shop` identity field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body when computing the HMAC that authenticates a webhook, but the `shop` (tenant) identity is taken from the unsigned `X-Shopify-Shop-Domain`/`shopify-shop-domain` header. The HMAC therefore verifies "this body was produced by Shopify," not "this body was produced by Shopify *for this shop*," breaking the intended binding `verified_bytes == acted_on_identity`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. The `shop` accessor is read straight from an HTTP header without being part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., the body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` validates only this body-bound HMAC before dispatching the (unauthenticated) `shop` value to the host application's handler: [4](#0-3) 

Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` *is* included in the signed payload used for OAuth-callback HMAC verification: [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" pattern: the equality the gem is supposed to enforce is `hmac_verified(shop, body) == true`, but what is actually enforced is `hmac_verified(body) == true` while `shop` is trusted independently and passed downstream as the tenant identifier in `WebhookMetadata`.

### Impact Explanation
Because only the body is signed, any webhook payload/HMAC pair genuinely issued by Shopify for one shop remains a valid `(body, hmac)` pair regardless of which `shop-domain` header value accompanies it. An attacker who can obtain one genuine webhook delivery (e.g., from their own store, from a shared/public app that emails/logs webhook payloads, or by intercepting their own app's webhook endpoint traffic) can resend the identical body and HMAC to the host application's webhook endpoint while substituting an arbitrary victim `shop-domain` header. `HmacValidator.validate` still passes because it never inspects `shop`, and `Registry.process` will hand the handler a `WebhookMetadata` object claiming the (attacker-chosen) victim shop, per-tenant data cross-contamination in the host application (cross-tenant access) since the gem's own signature check does not bind shop identity to the signed bytes.

### Likelihood Explanation
Exploitation requires the attacker to have captured at least one legitimately-signed webhook body/HMAC pair (trivially obtainable from their own installed app instance, since anyone can install most Shopify apps and receive real webhooks for their own shop), then replay it against the same app's public webhook endpoint with a forged `shop-domain` header for a different shop. No access to `api_secret_key`, tokens, or TLS interception is needed. This is a self-contained, deterministic bypass of the gem's tenant-binding guarantee, not a theoretical scenario.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signed material verified against the HMAC, or otherwise ensure the tenant-identifying header is bound to the same authenticated channel as the body before it is passed to the handler. If Shopify's webhook HMAC scheme is defined to only cover the body, this gem should document that `request.shop` is unauthenticated and must not be trusted for tenant attribution without additional verification (e.g., cross-checking that the shop actually exists in the app's session store as an installed shop, and rejecting/idempotency-checking by `webhook_id` to prevent replay).

### Proof of Concept
```ruby
require "shopify_api"

# Attacker installs the same app on their own shop and captures ONE real webhook
raw_body = '{"id":123,"note":"legit payload from attacker-shop"}'
real_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => "<valid base64 hmac captured from Shopify for attacker-shop.myshopify.com>",
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  "x-shopify-webhook-id" => "captured-id",
  "x-shopify-api-version" => "2024-01",
}

# Replay with the SAME body/hmac but a forged shop header
forged_headers = real_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# This still passes because HmacValidator only checks raw_body, not shop
ShopifyAPI::Webhooks::Registry.process(request)
# => Handler receives WebhookMetadata with shop == "victim-shop.myshopify.com"
#    even though the HMAC only proves the body, not the shop.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
