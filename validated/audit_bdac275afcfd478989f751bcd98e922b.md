### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then trusts the `shop` value taken from an HTTP header that is never included in that signature. This breaks the binding `shop authenticated == shop the payload actually belongs to`, letting anyone who can obtain one validly-signed webhook (e.g., by installing the app on their own free/dev store) relabel it as belonging to any other shop.

### Finding Description
`Utils::HmacValidator.validate` is the sole authentication check performed on an inbound webhook: [1](#0-0) 

It calls `validate_signature`, which computes the HMAC exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body — it does not include `topic`, `shop-domain`, `webhook-id`, or `api-version`: [3](#0-2) 

`shop` is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header with no cryptographic tie to the signed body: [4](#0-3) 

After the (body-only) HMAC check passes, `process` builds `WebhookMetadata` using this unauthenticated `request.shop` value and hands it directly to the app's registered handler as the tenant identifier: [5](#0-4) [6](#0-5) 

The identity equality that should hold is:
`shop the HMAC authenticates == shop attributed to the processed payload`

Because the HMAC is computed with the app-wide `Context.api_secret_key` (the same secret for every shop that installs the app) and covers only the body bytes, that equality does not hold: any body+HMAC pair valid for shop A's webhook remains a byte-for-byte valid HMAC when the `shop-domain` header is swapped to shop B's domain. The gem provides no way, and performs no check, to confirm the header's shop actually corresponds to the shop that generated the signed body.

### Impact Explanation
This is a cross-tenant identity confusion in the webhook processing pipeline of the gem itself, not something dependent on host-application misuse: the gem's own `Registry.process` treats `request.shop` as authenticated once `HmacValidator.validate` succeeds, but that header was never covered by the signature. An attacker who has installed the target app on any shop they control (a legitimate, free/dev install) can capture one genuine webhook (valid body + valid HMAC, signed by the shared `api_secret_key`), then replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim merchant's domain. `Registry.process` will accept the HMAC (it only checks the body) and dispatch `WebhookMetadata` with `shop` set to the victim, causing the app to process/store attacker-controlled data under the victim's tenant context — a cross-tenant access/data-integrity violation.

### Likelihood Explanation
Reachable by any unprivileged internet user who can install the target app on a shop they control (a normal, permitted action for any Shopify developer/dev store) and can send an arbitrary HTTP POST to the app's public webhook endpoint with forged headers. No access token, `api_secret_key`, or privileged account is required — only the ability to receive one webhook from their own store and replay it with a modified header, which any HTTP client can do.

### Recommendation
Bind the tenant identity to the signed content or to an out-of-band trusted channel rather than to an unauthenticated header:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signed payload used for `to_signable_string`, or
- After HMAC validation, cross-check `request.shop` against the shop associated with the specific webhook subscription (e.g., by looking up the webhook by `webhook_id` via the Admin API, or requiring the host app to validate the shop is one it has an active session/installation for) before dispatching to `WebhookHandler#handle`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` (a shop they control) and triggers any subscribed webhook topic (e.g., `orders/create`) to receive a genuine webhook delivery: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the same body `B` and same `H` to the app's public webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares it to `H` — this still matches because the signature never covered the shop header: [7](#0-6) 
4. Validation succeeds; `process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...)` and invokes the app's handler, which now processes attacker-supplied data attributed to the victim shop: [5](#0-4)

### Citations

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
