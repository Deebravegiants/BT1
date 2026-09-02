### Title
Webhook `shop-domain` Header Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity handed to a merchant's webhook handler from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC that `Registry.process` validates only covers the raw request body. The identity binding `HMAC verified == (body, shop)` that the gem's callers implicitly rely on actually only holds for `HMAC verified == (body)`.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhook requests that string is simply the raw body: [1](#0-0) [2](#0-1) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end

sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

`Registry.process` only checks the HMAC of the body before dispatching to the handler, and passes `request.shop` straight through as the trusted tenant identifier: [3](#0-2) 

```ruby
sig { params(request: Request).void }
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`WebhookMetadata#shop` is a plain `String` field passed unmodified from the unauthenticated header into the merchant-facing `WebhookHandler#handle` interface: [4](#0-3) 

Because `shop-domain` is not part of the signable string, `HMAC(body)` is valid for *any* value of the `shop-domain` header. An attacker who can obtain one valid `(body, hmac)` pair — trivially, by installing/using the same app on their own store (a store they legitimately control) and capturing the webhook Shopify sends them, or by observing any webhook whose body content is predictable/generic (e.g. `{}` payloads, or payloads with attacker-influenced content such as order/customer webhooks for their own store) — can resend that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept it as valid (the HMAC still matches) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

This breaks the equality the gem is implicitly asserting to callers: `hmac_valid(request) => (body, shop) genuinely originated together from Shopify for that shop`. In reality `hmac_valid(request) => body originated from Shopify (for some shop the attacker controls)`, and `shop` is fully attacker-controlled.

### Impact Explanation
This is a cross-tenant identity-binding break: an app that uses `request.shop`/`WebhookMetadata#shop` (as the documented usage pattern instructs, e.g. to look up the appropriate `Session`/access token for that shop, or to key GDPR/mandatory webhook processing like `shop/redact`) can be tricked into processing attacker-supplied webhook content under a victim shop's identity, or into performing actions scoped to the wrong tenant. Depending on handler logic this can lead to cross-tenant data corruption, incorrect GDPR-redaction targeting, or triggering shop-scoped side effects for a shop the attacker does not control — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is moderate: the attacker needs at least one legitimately-signed `(body, hmac)` pair, which is straightforward to obtain by installing the app on their own store (many apps are installed by arbitrary merchants/dev stores) and capturing any webhook delivery, then replaying it against the same endpoint with a forged shop header. No secret key or privileged credentials are required — only a normal, unprivileged internet-reachable webhook endpoint and a store the attacker legitimately controls.

### Recommendation
Include the shop domain (and ideally the webhook topic/id) in the signable string used for HMAC verification, or independently bind/verify `request.shop` against a value that is itself covered by the signature (e.g. compare it to the shop associated with the session/context that is expected to receive this webhook) before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the app (or otherwise trigger a webhook delivery) on `attacker-shop.myshopify.com`; capture the raw POST body `B` and the `x-shopify-hmac-sha256` header `H` that Shopify sends (valid because HMAC is computed only over `B` with the app's shared secret).
2. Replay the request to the app's webhook endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only checks `H` against `B` [1](#0-0)  — validation succeeds.
4. The registered handler receives `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [5](#0-4) , processing attacker-controlled content under the victim shop's identity.

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
