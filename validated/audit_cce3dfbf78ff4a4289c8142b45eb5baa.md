### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), `topic`, `webhook_id`, and `api_version` used to dispatch a webhook to the merchant's application handler entirely from unauthenticated HTTP headers, while the HMAC signature verified in `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body. The equality the code implicitly assumes — "bytes verified == bytes that determine the tenant" — does not hold, breaking the identity binding between the authenticated payload and the routing metadata handed to the app's webhook handler.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it against the provided `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body` — the request headers are excluded entirely from the signed data: [2](#0-1) 

However, `shop`, `topic`, `webhook_id`, and `api_version` — the fields used to route the webhook and identify which merchant/tenant it belongs to — are all read straight from headers (`shopify-shop-domain`, `shopify-topic`, etc.), none of which participate in the HMAC computation: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop` and `request.topic` (unauthenticated headers) to build the `WebhookMetadata` passed to the handler: [4](#0-3) 

Because the signature only binds the body bytes, and the shop/topic identity fields are parsed from headers outside that signed scope, `hmac_valid(body) == true` does not imply `shop_header == actual_originating_shop`. An attacker who can influence or replay the header set on a request that carries a *previously valid* `(body, hmac)` pair (e.g., a network intermediary, a shared/misconfigured ingress, or a malicious co-tenant capable of relaying a webhook payload through the app's public endpoint with altered headers) can cause the application to process an event under a victim shop's identity while `Registry.process` still reports the HMAC as valid, since the check never touches the header.

### Impact Explanation
This breaks the tenant/shop authentication boundary that `Registry.process` is supposed to enforce before invoking the merchant's handler: the handler receives `WebhookMetadata.shop` that is not actually bound to the cryptographically verified payload, enabling cross-tenant data confusion (an app could apply another shop's webhook body under an attacker-chosen shop identity, or process a payload under the wrong topic/webhook_id). This matches the "cross-tenant access" class of impact called out in scope.

### Likelihood Explanation
Exploitation requires the attacker to control or manipulate the raw HTTP headers of a request reaching the app's webhook endpoint while reusing a body/HMAC pair, e.g., via a proxy, load balancer misconfiguration, or a scenario where the endpoint is reachable with attacker-supplied headers alongside a replayable valid body. This is a real design gap in this gem's verification method (headers are trusted anywhere they're consumed, `to_signable_string` never includes them), rather than a theoretical concern, since the gem provides no mechanism at all to bind header-derived routing data to the signature.

### Recommendation
Either include the shop/topic/webhook_id headers in the signable string used for HMAC computation, or independently verify `request.shop` against the shop associated with the session/expected recipient before dispatching to the handler, so the fields used for tenant routing are cryptographically bound to the same integrity check as the payload:
```ruby
def to_signable_string
  "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
end
```

### Proof of Concept
1. Capture a legitimate webhook delivery for `shop-a.myshopify.com` consisting of `raw_body` `B` and its valid `x-shopify-hmac-sha256` header `H` (computed by Shopify over `B` only).
2. Replay/forward the same `(B, H)` pair to the app's webhook endpoint but substitute the `x-shopify-shop-domain` header with `shop-b.myshopify.com` (a different, victim tenant).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `B` — validation succeeds because `to_signable_string` never included the shop header: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)`, i.e., the body from shop A is now processed under shop B's identity, despite the "HMAC valid" check passing.

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
