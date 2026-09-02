This confirms the vulnerability. The `ShopifyAPI::Webhooks::Request#topic`, `#shop`, and `#webhook_id` are all read directly from unauthenticated HTTP headers, while `to_signable_string` (used by `HmacValidator.validate`) only covers `@raw_body`.This confirms the finding: `Registry.process` trusts `request.topic` and `request.shop` (both derived from headers) to dispatch to a handler and identify the tenant, while `HmacValidator.validate` only authenticates `@raw_body`.### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by HMAC verification, allowing tenant/topic spoofing of an authentic webhook payload - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field, `topic`, and `webhook_id` directly from unauthenticated HTTP headers, while `Utils::HmacValidator.validate` only authenticates the raw request body. This breaks the intended identity binding `hmac_signed_bytes == bytes_the_gem_trusts_for_tenant_and_topic_dispatch`. This mirrors the bug class in the reported analog: a field that is acted upon (here, the `shop` used for tenant dispatch) is not covered by the integrity check (here, the HMAC), so it can be substituted independently of the signed content.

### Finding Description
`Utils::HmacValidator.validate(verifiable_query)` computes the HMAC over `verifiable_query.to_signable_string` and compares it against the received `hmac`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `Request#shop`, `#topic`, and `#webhook_id` are read straight from HTTP headers, which are never part of the signed bytes: [3](#0-2) 

`Registry.process` uses `request.topic` to select the handler and passes `request.shop` (and `request.webhook_id`) straight into `WebhookMetadata`, which is what the host application uses to attribute the payload to a tenant: [4](#0-3) [5](#0-4) 

The equality that should hold is: `hmac == HMAC(secret, shop || topic || raw_body)` binding the tenant and topic to the payload. Instead the gem verifies `hmac == HMAC(secret, raw_body)` only, so `shop`/`topic`/`webhook_id` are trusted independent of what was actually signed — exactly analogous to `getOperatorIdForAddress` remaining bound to a stale/uncontrolled identity because the update path didn't clear the coupled field.

### Impact Explanation
An attacker who legitimately receives one authentic Shopify webhook for their own shop/topic (trivial to obtain — install any app, install their own test app, or use a public app's own store) has a raw body + valid HMAC pair signed with the target app's `api_secret_key`... but crucially, the HMAC never encodes the shop or topic. The attacker can replay that exact `raw_body`+`hmac` combination to the target app's webhook endpoint while freely rewriting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers, since `HmacValidator.validate` will still pass (it only checks `raw_body`). This lets an unprivileged internet user cause the host application to process forged/mismatched tenant attribution or topic dispatch (e.g., attribute a webhook payload to a victim shop, or trigger a handler for a topic the payload was never actually generated for) while the gem reports the request as validly authenticated. This crosses a tenant boundary (cross-tenant confusion) built into the trusted `shop` field the app relies on for data isolation, which maps to the "Critical - cross-tenant access" category.

### Likelihood Explanation
Any external party who can capture one legitimate webhook delivery from the target app's own secret (e.g., via a store they control that has installed the app) can perform this replay without ever needing the app's `api_secret_key`, an access token, or any privileged account. The only requirement is observing the webhook HTTP request once (headers are plaintext, body is JSON), which is straightforward from a network log or a controlled receiving endpoint. No cryptographic secret needs to be broken.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed/verified material, or at minimum verify them against out-of-band trusted state (e.g., only accept `shop` values previously associated with a real OAuth/installation session, and reject if body-encoded shop identifiers, when present in the payload's `shop_id`/`shop_domain`, differ from the header value). Since Shopify's webhook HMAC scheme signs only the body, the safer mitigation within this gem is to cross-check `raw_body` JSON's own shop/domain fields (when Shopify includes them) against the header-derived `shop`, and to document/require host applications not to trust `WebhookMetadata#shop` as a sole tenant boundary without additional verification.

### Proof of Concept
1. Attacker installs (or already has) the target app on their own store `attacker.myshopify.com`, triggering a legitimate webhook delivery for topic `orders/create` with a real HMAC signed by the app's `api_secret_key`.
2. Attacker captures the raw POST body and the `X-Shopify-Hmac-Sha256` header from that delivery.
3. Attacker replays the same raw body and HMAC header to the app's webhook endpoint, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or a different registered topic if payload shape overlaps)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — this matches, so validation succeeds: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the payload/HMAC were never generated for that shop, causing the host application to process attacker-controlled data under the victim's tenant identity.

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
