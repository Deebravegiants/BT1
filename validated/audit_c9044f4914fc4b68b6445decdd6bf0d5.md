### Title
Webhook Shop/Topic/Webhook-ID Headers Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the shop identity (`shop-domain`), `topic`, and `webhook-id` headers are read directly from unauthenticated HTTP headers and never included in the HMAC-signed material. `Registry.process` trusts these header-derived values as the authoritative shop/topic identity once the HMAC check passes, breaking the intended binding `shop authenticated == shop acted upon`.

### Finding Description
`HmacValidator.validate` calls `verifiable_query.to_signable_string` to compute the expected signature and compares it to the provided `hmac`, exactly as it does for OAuth's `AuthQuery`: [1](#0-0) 

For webhooks, `to_signable_string` returns *only* `@raw_body`: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are read straight from HTTP headers, independent of the signed payload: [3](#0-2) 

`Registry.process` validates only the HMAC of the request, then unconditionally trusts `request.shop` and `request.topic` (both outside the signed material) to build the data handed to the application's webhook handler: [4](#0-3) 

Because the shop identity is never covered by the HMAC, the equality the gem is supposed to guarantee — "the shop whose secret produced this signature" == "the shop the handler is told this webhook belongs to" — does not hold. Anyone in possession of one valid `(raw_body, hmac)` pair for the app's secret (e.g., a real merchant who installed the app and captured one of their own genuine webhook deliveries) can replay that exact body/signature pair to the app's public webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header for a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks `@raw_body`, and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This breaks the shop-authentication binding the HMAC is meant to provide and results in cross-tenant confusion: an app's webhook handler (which typically keys persistence, GDPR redaction, or business logic off `WebhookMetadata#shop`) can be made to act on/attribute data to a shop that never sent it, using a signature that was never generated for that shop. This falls under the cross-tenant access impact category.

### Likelihood Explanation
Likelihood is low-to-moderate: exploitation requires the attacker to already hold one legitimately-signed `(body, hmac)` pair for the app (obtainable by installing the app on their own shop, a low bar for a "merchant" attacker), plus the ability to POST directly to the app's public webhook endpoint with forged headers, which is generally reachable since webhook endpoints are public HTTP endpoints.

### Recommendation
Include the shop domain, topic, and webhook id in the signable string (or otherwise independently bind these header values to the same secret/signature), so that `to_signable_string` cannot be satisfied by a raw body alone; e.g.:
```diff
def to_signable_string
- @raw_body
+ "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
end
```
(with corresponding changes needed on the receiving/computation side agreement), or alternatively document/require that host apps independently verify the shop header against their own tenant registry before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and captures one genuine webhook delivery: raw body `B` with header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `api_secret_key`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker POSTs to the app's public webhook endpoint with the *same* body `B` and signature `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `Utils::HmacValidator.validate(request)` computes `compute_signature(request.to_signable_string, secret)` where `to_signable_string == B`; it matches `H`, so validation passes: [2](#0-1) 
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process/store data under the victim shop's identity despite the signature never having been produced for that shop: [4](#0-3)

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
