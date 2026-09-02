### Title
Webhook HMAC validation excludes shop-domain, topic, and webhook-id headers, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop-domain`, `topic`, and `webhook-id` headers — which are used unmodified to identify the tenant and dispatch the event to the app's handler — are never included in the signed material. Any party capable of capturing one legitimately-signed webhook body (e.g., from their own shop's traffic) can replay that exact body/HMAC pair while substituting arbitrary values for `shop-domain`, `topic`, and `webhook-id`, and the gem will treat the forged request as authentic and dispatch it under the attacker-chosen tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string`: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` checks only this body-only HMAC and then dispatches to the handler using the unauthenticated `request.shop` and `request.topic` values, which are read straight from HTTP headers: [3](#0-2) [4](#0-3) 

The identity binding that should hold is:
`HMAC(secret, signed_bytes) == received_hmac` **and** `signed_bytes ⊇ {shop, topic, webhook_id}`.

In this implementation, `signed_bytes = raw_body` only, so the equality that actually holds is `HMAC(secret, raw_body) == received_hmac`, while `shop`, `topic`, and `webhook_id` are trusted **without being covered by the signature**. This is exactly the "field acted on but not covered by the HMAC" class of bug: the bytes verified (raw body) are not the bytes acted upon for tenant/topic dispatch (headers).

### Impact Explanation
Any entity that can observe one genuinely Shopify-signed webhook payload for *any* shop (e.g., an app's own merchant capturing their own store's webhook traffic, since webhook bodies for common topics are often near-identical/predictable, e.g. empty-body test webhooks or repeated JSON shapes) can replay that body+HMAC with a forged `shop-domain` header pointing at a different tenant and/or a forged `topic`/`webhook-id`. `Registry.process` will pass HMAC validation and invoke the app's registered handler believing the event genuinely originated from the victim shop and/or topic. Depending on how the host application's handler uses `WebhookMetadata#shop`/`#topic` (e.g., to look up tenant records, trigger uninstall/GDPR flows, or update per-shop state), this crosses the tenant boundary — an unprivileged party can inject events attributed to a shop they do not control. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one validly-signed webhook body (trivial for their own shop, since they are a legitimate merchant using the app) and the ability to POST directly to the app's public webhook endpoint with custom headers (standard for any internet-reachable webhook receiver, not gated by anything the gem enforces). No access to `api_secret_key` is needed since the attacker replays a signature that was already computed by Shopify for genuine traffic; only the header values are forged. This is a straightforward replay once one real signed payload is captured.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` in the signed byte string that `HmacValidator` verifies, or otherwise cryptographically bind them to the HMAC (e.g., verify against a canonicalized string of `topic|shop|webhook_id|raw_body`). Alternatively, document and enforce that host applications must independently corroborate `shop`/`topic` against the recipient's own registration/session store rather than trusting headers implicitly.

### Proof of Concept
1. Attacker's own store `attacker.myshopify.com` receives a genuine Shopify webhook with body `{}` and header `x-shopify-hmac-sha256: <valid HMAC over "{}">`.
2. Attacker resends this exact body and HMAC to the app's webhook endpoint but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: shop/redact` (or any registered topic)
   - `x-shopify-webhook-id: <arbitrary>`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, "{}")`.
4. The handler for that topic is invoked with `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", body: {}, ...)`, causing the app to process a forged event as if it originated from `victim-shop.myshopify.com`.

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
