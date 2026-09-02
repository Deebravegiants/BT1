### Title
Webhook shop identity (`shop-domain` header) is not covered by the HMAC signature, allowing cross-tenant shop spoofing on webhook delivery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the merchant's `WebhookHandler` from the raw `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, but `Registry.process` only validates the HMAC over `to_signable_string`, which is defined as the raw request body alone. The `shop`, `topic`, `api_version`, and `webhook_id` headers are never part of the signed payload, so a valid HMAC only proves the body was produced by the app's shared secret — it proves nothing about which shop the webhook is "for."

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the supplied `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is hard-coded to the raw body only: [2](#0-1) 

Meanwhile, the `shop` accessor used as the tenant key for the callback is read straight from the (unsigned) HTTP header: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then constructs `WebhookMetadata` (the payload delivered to the merchant's business logic) directly from these unauthenticated headers: [4](#0-3) [5](#0-4) 

This breaks the identity binding: `hmac(body) == hmac(body)` is checked, but the equality that actually matters for tenant isolation, `shop_header == shop_that_produced_this_body`, is never enforced by the gem. Because every shop that has the app installed shares the same `client_secret` (the same HMAC key is used for all merchants of a given app), a webhook body legitimately signed for Shop A's data will produce a byte-identical, still-valid HMAC no matter which `shop-domain` header accompanies it. An attacker who controls their own shop (an ordinary, unprivileged merchant who installed the app — no `api_secret_key`, access token, or special privilege required) can:

1. Trigger/capture a legitimate webhook delivery for their own shop (raw body + valid HMAC), or replay one they already receive from their own store, and
2. Re-POST the same `raw_body`/`hmac` pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to point at a different, victim shop that also uses the same app.

`Registry.process` will accept it (HMAC over body matches) and hand the handler a `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-chosen `body`. Any host application that trusts `WebhookMetadata#shop` as the tenant key (the intended and documented usage pattern) will store/act on attacker-supplied data under the victim shop's identity — a cross-tenant data-injection/confusion primitive entirely within this gem's own webhook-processing code path, not caused by host misuse.

### Impact Explanation
This is a cross-tenant boundary violation reachable without any credential belonging to the app or the victim: no `api_secret_key`, no access token, no privileged account, only an attacker who is themself an ordinary merchant of the multi-tenant app (or who can otherwise obtain one legitimately-signed body+hmac pair, e.g. from their own shop's webhook feed). The gem's own `Registry.process`/`WebhookMetadata` construction fails to bind the cryptographically verified bytes (`raw_body`) to the claimed tenant (`shop-domain` header), which is exactly the "bytes verified vs. identity trusted" gap called out as in-scope for this analysis. This meets the High bar as a scope/identity-binding check that answers permissively and enables cross-tenant access to a different merchant's webhook processing pipeline.

### Likelihood Explanation
Moderate-to-high: any developer of a multi-tenant Shopify app using this gem's webhook helpers (`ShopifyAPI::Webhooks::Registry.process`, `Request`, `WebhookMetadata`) is exposed as long as they trust `data.shop` from `WebhookMetadata` — which is the documented/expected contract of this API. No secret material or advanced tooling is needed; only the ability to send an HTTP POST with attacker-controlled headers and a body/HMAC pair obtainable from the attacker's own legitimately-installed shop.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification (or otherwise cryptographically bind them to the body, e.g. by hashing header+body together), so that a valid signature also attests to the specific shop and topic the webhook was issued for. Alternatively, require callers to supply the expected shop out-of-band (already known installed shop) and have `Registry.process` reject webhooks whose header `shop` doesn't match an app-provided allow-list/expected shop, rather than trusting the header unconditionally.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both sharing the same app `client_secret`.
2. Attacker triggers/captures a webhook delivery to their own endpoint (or replicates the mechanism) for `attacker-shop.myshopify.com`, obtaining `raw_body` and its valid `X-Shopify-Hmac-Sha256` value.
3. Attacker POSTs this exact `raw_body` + `X-Shopify-Hmac-Sha256` to the target app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(secret, raw_body)` — this passes because the body/HMAC pair is genuinely valid for that secret.
5. `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's raw_body>, ...)` is passed to the host app's handler, which now processes attacker-controlled body content attributed to `victim-shop.myshopify.com`.

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
