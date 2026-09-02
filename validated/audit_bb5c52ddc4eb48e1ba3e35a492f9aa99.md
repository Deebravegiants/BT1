## Title
Webhook `shop`, `topic`, `webhook-id` and `api-version` values are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and passed on to the app's webhook handler as trusted, verified data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)` before dispatching to the handler [2](#0-1) . `HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header value [3](#0-2) . Meanwhile, `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all pulled straight from headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) with no cryptographic binding to the signed body [4](#0-3) . After HMAC validation succeeds, `Registry.process` builds a `WebhookMetadata` struct directly from these unverified header values and hands it to the host app's handler as authoritative tenant/topic context [5](#0-4) [6](#0-5) .

This breaks the identity binding: `shop_header == shop_used_by_handler` is enforced, but `shop_header` is never checked against `HMAC(body, secret)`. The binding that should hold — "the tenant asserted by the signed payload equals the tenant the handler acts on" — does not, because the signature only proves body integrity, not header integrity.

### Impact Explanation
An attacker who has installed the same multi-tenant app on their own store (a normal, unprivileged action) can trigger a legitimate webhook to their own endpoint capture logs (e.g., `products/update`), obtaining a body + valid `X-Shopify-Hmac-Sha256` pair signed with the app's shared `client_secret`. Because the signature never covers the `shop`, `topic`, or `webhook-id` headers, the attacker can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim merchant's domain (and/or a different `topic`). `Registry.process` will pass HMAC validation (body is unchanged) and dispatch `WebhookMetadata` claiming the data belongs to the victim shop and/or a different topic than what was actually signed. If the host application (as documented/intended by this gem) uses `data.shop` to attribute the webhook body to a specific merchant's records (the gem's own documented integration pattern), the attacker can inject attacker-controlled data attributed to another tenant — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Moderate. It requires the attacker to be a legitimate app user on some tenant (trivial for any public multi-tenant Shopify app) and to control the ability to trigger a webhook with attacker-influenced body content (e.g., updating their own product/order), then replay the captured request with altered headers to the same public webhook endpoint. No secrets, tokens, or privileged access are required — only standard installer-level interaction with a multi-tenant app that uses this gem's webhook verification as its sole authentication mechanism.

### Recommendation
- Short term: Include `shop`, `topic`, and `webhook_id` in the value being verified, or independently validate `request.shop`/`request.topic` against values already known/authorized for that HMAC-signed delivery (e.g., cross-check against Shopify's `X-Shopify-Webhook-Id` via a replay/idempotency store), and document clearly that header fields are unauthenticated.
- Long term: Extend `VerifiableQuery`/`HmacValidator` so the signable string composition binds all header fields the application is expected to trust (shop, topic, webhook id) rather than only the raw body, matching the general principle of binding all consumed identity fields to the authenticated signature.

### Proof of Concept
1. Attacker installs the multi-tenant Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a `products/update` webhook with an attacker-crafted product body; Shopify sends a POST to the app's webhook endpoint with headers:
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `X-Shopify-Topic: products/update`
   - `X-Shopify-Hmac-Sha256: <valid HMAC over body>`
3. Attacker captures this full raw request (this is their own webhook, so capturing outbound traffic to their own server is trivial).
4. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` header to the same webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` recomputes the HMAC over the (unchanged) body and it matches, per `lib/shopify_api/utils/hmac_validator.rb` line 26-31.
6. `Registry.process` dispatches `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` to the handler, which the host app treats as an authenticated event for the victim tenant, per `lib/shopify_api/webhooks/registry.rb` lines 190-199.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
