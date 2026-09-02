### Title
Webhook `shop` (and topic/api-version/webhook-id) identity fields are not covered by HMAC verification, allowing cross-tenant impersonation via header substitution on a replayed signed payload - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw JSON body. The `shop` (and `topic`, `api_version`, `webhook_id`) values that are handed to the host application's webhook handler as the tenant identity are read directly from HTTP headers that are **not** included in the HMAC-signed content. Anyone who possesses one validly-signed webhook payload for their own shop (which every merchant installing the app legitimately receives) can resend that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header to claim the payload originated from a different shop, and the signature check will still pass.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from headers, none of which are part of the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then forwards `request.shop` (an unauthenticated header value) directly to the handler as the tenant identity, without any binding between it and the HMAC-covered body: [3](#0-2) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, i.e. the body — the identity headers never enter the comparison: [4](#0-3) 

The binding that is broken is:
`shop header value used by the host app` ≠ `shop bytes verified by HMAC`

Because `shop` is not part of the signed material, an attacker who is a legitimate merchant/installer of the app (an unprivileged internet user with respect to *other* tenants) can capture one of their own genuine webhook deliveries (valid body + valid `x-shopify-hmac-sha256`) and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. The gem will report `Utils::HmacValidator.validate(request)` as `true` and hand the handler a `WebhookMetadata` claiming to be from the victim shop while carrying attacker-chosen body content, since the body's HMAC is still valid (it was never tied to the shop).

### Impact Explanation
This breaks the shop-identity binding that host applications are expected to rely on when routing webhook data to per-tenant storage/actions (documented usage is `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, body: ..., ...))`, and apps are expected to treat `data.shop` as authenticated). An attacker can inject attacker-controlled webhook body content attributed to an arbitrary victim shop, i.e. cross-tenant data injection through the app's own webhook processing pipeline — a cross-tenant access impact within the boundary that this gem is responsible for verifying (HMAC authenticity of the webhook including its identity claims).

### Likelihood Explanation
Likelihood is high: any merchant who installs the app receives real signed webhooks for their own shop, giving them body/HMAC pairs usable in the replay. No secrets, tokens, or privileged access are required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-controlled headers, which is exactly the threat model of an "unprivileged internet user."

### Recommendation
Bind the shop (and topic/webhook-id/api-version) to the HMAC-verified content rather than trusting unauthenticated headers: either require the app to independently confirm the `shop-domain` header against a known/registered shop before dispatching, or extend the signable string / verification step in `ShopifyAPI::Webhooks::Request` and `HmacValidator` to incorporate the identity headers so that a mismatch invalidates the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body B>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: B  (JSON payload, can be crafted by placing malicious order data before triggering the webhook, or captured verbatim)
   ```
2. Attacker resends the identical request to the app's webhook endpoint, only changing the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
   (`x-shopify-hmac-sha256` and body `B` unchanged.)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC only covers `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, causing the host app to process attacker-controlled content under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
