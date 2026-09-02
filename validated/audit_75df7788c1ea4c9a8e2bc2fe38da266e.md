Confirmed. The vulnerability is clear and reachable entirely within in-scope files (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/webhook_handler.rb`, `lib/shopify_api/utils/hmac_validator.rb`). The `Registry.process` explicitly claims "this will verify the request did indeed come from Shopify" per the docs, but the `shop` (and `topic`/`webhook_id`/`api_version`) fields it hands to the handler as authenticated are never part of the HMAC-covered bytes.

### Title
Webhook shop/topic/webhook_id are trusted from unauthenticated headers while HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, which only verifies the raw request body against the HMAC signature. The `shop`, `topic`, `webhook_id`, and `api_version` fields — read straight from attacker-visible/attacker-settable HTTP headers — are never included in the signed bytes, yet they are handed to the app's `WebhookHandler` as if fully authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature purely over `to_signable_string`: [2](#0-1) 

But `Request#shop`, `#topic`, and `#webhook_id` are read from headers, none of which participate in `to_signable_string`: [3](#0-2) 

`Registry.process` validates only the HMAC, then forwards these unauthenticated header values directly into `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

The equality this gem's own documentation claims to guarantee is:
`shop asserted in WebhookMetadata == shop that actually produced the signed body`

But the code only proves:
`HMAC(body, api_secret_key) == received_hmac`

It never proves the `shop-domain` header corresponds to the shop that generated that body. Critically, `Context.api_secret_key` (the app's `client_secret`) is a single value shared across **every shop that installs the app** — it is not shop-specific. That means any merchant who installs the app receives real webhook deliveries carrying a valid `X-Shopify-Hmac-Sha256` signature computed with that same shared secret over a body whose content the merchant substantially controls (e.g. a `products/update` webhook body reflects a product title/body_html the merchant just edited in their own store). Because the signature never binds to `shop-domain`, a malicious merchant can:
1. Edit their own store data to produce an attacker-chosen JSON body inside a real, Shopify-delivered, validly-signed webhook.
2. Capture that `(raw_body, hmac)` pair.
3. Replay the exact same body/hmac to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain.

The gem will report `Utils::HmacValidator.validate(request)` as `true` (body/hmac untouched) and hand `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_controlled_json, ...)` straight to the host app's handler, which per the gem's own documented usage pattern uses `data.shop` to determine which tenant's local records to update: [6](#0-5) 

This is a genuine root-cause defect in `shopify_api` itself, not a misuse of a documented API: the library's public contract via `Registry.process`/`Utils::HmacValidator.validate` explicitly promises verification of webhook authenticity ("This will verify the request did indeed come from Shopify") while leaving the shop-binding field entirely outside that verification.

### Impact Explanation
This breaks the tenant-identity binding at the heart of webhook processing: an attacker who is a legitimate (even free/trial) merchant of the app can forge webhooks that the host application will process as if they originated from an arbitrary victim shop, with attacker-chosen body content constrained only by what fields they can influence in their own store's data. Depending on the handler's logic (as shown in the gem's own documented example, which keys work off `data.shop`), this enables cross-tenant data injection/corruption — writing attacker-controlled data into another merchant's records, or triggering shop-scoped actions (e.g. `app/uninstalled`, `shop/redact`) against a victim tenant. This matches the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Any developer who installs the app in their own shop can trivially capture their own valid `(body, hmac)` pairs — no secret key, TLS interception, or privileged access is needed, since the attacker is simply an ordinary merchant receiving webhooks that Shopify sends them for their own shop. Replaying an HTTP POST to the app's public webhook endpoint with a modified header is trivial. The only constraint is crafting the desired JSON content by manipulating their own store data, which is often sufficient for meaningful attacks (e.g., product/customer/order webhooks reflect editable fields).

### Recommendation
Bind the shop identity to the signature verification, not just the raw body. Options:
- Require host apps to verify the `shop-domain` header against a known/registered shop for that webhook subscription (e.g., cross-check against the shop that this specific webhook `topic`+`webhook_id` was registered for) before trusting `data.shop`.
- Document explicitly and prominently that `data.shop` in `WebhookMetadata` is **not** authenticated by the HMAC check and must not be used to select tenant-scoped code paths without additional verification.
- Where feasible, include the header value in the signable payload used for verification, or provide a per-shop webhook secret binding.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and subscribes it to `products/update` webhooks.
2. Attacker edits a product's `body_html`/title in `attacker-shop` to contain attacker-desired payload content, triggering Shopify to POST a `products/update` webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid signature over that body computed with the app's shared client_secret>`.
3. Attacker intercepts/logs this request from their own network/proxy (fully legitimate — it is their own webhook).
4. Attacker replays an HTTP POST to the same webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against `hmac` — both unchanged. [7](#0-6) 
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-crafted product data>, ...)` and processes it as an authentic update for `victim-shop`, per the gem's documented handler contract.

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
