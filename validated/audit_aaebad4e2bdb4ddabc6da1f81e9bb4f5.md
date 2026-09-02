## Finding: Webhook shop-domain header is not covered by the HMAC signature, breaking the shop⇄payload binding

### Title
Webhook `shop` identity is trusted from an unauthenticated header while only the raw body is HMAC-verified - (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content as the raw request body only, while the shop identity (`shop-domain` header) used to route/process the webhook is taken from an HTTP header that is never included in the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` as the tenant identity passed to the app's handler, even though that value was never bound to the signature that was verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from an HTTP header, independent of the signed content: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (i.e., the body) against the HMAC: [3](#0-2) 

`Registry.process` verifies the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, trusting it as the authoritative tenant for the handler: [4](#0-3) 

`WebhookMetadata.shop` is documented and intended to be used by the host application as the shop identity for the delivered payload: [5](#0-4) [6](#0-5) 

The broken identity binding, expressed as an equality that should hold but does not:
`shop_bound_by_HMAC(raw_body) == shop_used_by_handler(header)`

Both sides are computed independently — the left side doesn't exist at all, since `shop-domain` is never part of the signed content — so the equality can trivially be violated by supplying a genuine `(body, hmac)` pair together with an arbitrary `shop-domain` header.

### Impact Explanation
An attacker who legitimately installs the app on their own shop (any unprivileged internet user can create a free Shopify dev shop and install a public app) can trigger any webhook topic on their own shop to obtain a genuine `(raw_body, hmac)` pair signed with the app's real secret. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim merchant's shop domain. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` forwards `shop: <victim-shop>` to the app's handler as if the event genuinely originated from the victim tenant. Since the documented, expected usage pattern (per `docs/usage/webhooks.md`) is for the host app to key its per-tenant persistence/queueing directly off `data.shop`, this allows cross-tenant confusion/injection of attacker-controlled webhook bodies attributed to a victim shop — a cross-tenant boundary violation stemming entirely from this gem's own `Request`/`Registry` design, not from host misuse.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to obtain at least one genuine, freshly-signed `(body, hmac)` pair (trivially achievable by installing the app on an attacker-controlled shop and triggering any subscribed webhook topic), and then replay it with a forged `shop-domain` header value. No access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signable content, or otherwise cryptographically bind them, so that `Utils::HmacValidator.validate` fails if any of those header-derived fields are altered relative to what Shopify actually signed. At minimum, document prominently that `data.shop` in `WebhookMetadata` is not cryptographically authenticated and must be cross-checked by the host application against a known/installed-shop list before being used as a tenant key.

### Proof of Concept
1. Install the app on an attacker-controlled test shop `attacker.myshopify.com`; trigger a subscribed webhook topic (e.g. `orders/create`) to receive a legitimate webhook delivery with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
2. Replay the exact same `raw_body` and `shopify-hmac-sha256` value to the app's webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` accepts it because required headers are present; `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's body>, ...)`, and the host app (following the documented pattern) processes/enqueues it as an event for `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
