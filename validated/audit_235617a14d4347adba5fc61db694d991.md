Confirmed. The vulnerability is solid and well-supported by the code.

### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` fields are read directly from unauthenticated HTTP headers and are never part of the signed bytes. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then blindly trusts the header-derived `shop` when constructing `WebhookMetadata` passed to the app's handler, breaking the binding "shop attributed to a webhook == shop that produced/signed that webhook."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, independent of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string` (the body): [3](#0-2) 

`Registry.process` validates the HMAC and then forwards the header-derived, unauthenticated `request.shop` straight into `WebhookMetadata` given to the app handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` const with no further verification: [5](#0-4) 

Because the HMAC covers only the body bytes, `(body, hmac)` is a valid pair for *any* shop header value, as long as it was originally signed with the app's `api_secret_key` over that body. An unprivileged internet user can:
1. Install the target app on their own (attacker-controlled) shop via the normal, unprivileged OAuth flow.
2. Trigger a webhook delivery (e.g., `products/update`) with body content of their choosing, obtaining from Shopify a genuinely valid `(raw_body, hmac)` pair signed with the app's real `api_secret_key`.
3. Replay that exact `raw_body` and `hmac` to the app's public webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain (e.g., `victim-shop.myshopify.com`).
4. `HmacValidator.validate` still succeeds (body unchanged, hmac matches), and `Registry.process` invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and attacker-chosen `body`.

The equality broken is: `shop authenticated by the HMAC == shop attributed to the webhook by Registry.process`. The gem lets these diverge because only the body — never the tenant identifier — is bound by the signature.

### Impact Explanation
This is a cross-tenant confusion primitive: an unprivileged attacker who merely installs the app on their own store can inject arbitrary attacker-chosen webhook payloads that the host application will process as if they originated from any other shop of the attacker's choosing (a real merchant using the app), since nothing in the signed bytes ties the payload to a specific tenant. Depending on how the host app's `WebhookHandler` implementations use `data.shop` (e.g., looking up/updating that shop's session, inventory, or business data), this can lead to cross-tenant data corruption, unauthorized state changes attributed to another merchant, or triggering merchant-specific side effects (emails, order actions, uninstall handling) under a victim's identity.

### Likelihood Explanation
Likely and low-effort: no special access, credentials, or `api_secret_key` knowledge is required. An attacker only needs their own (attacker-owned) legitimate app installation — a normal unprivileged merchant onboarding step — to mint valid `(body, hmac)` pairs, and then a single crafted HTTP replay with a rewritten header to any host app whose handlers trust `WebhookMetadata#shop` for tenant-scoped logic.

### Recommendation
Include the tenant-identifying header(s) (`shop-domain`, and ideally `topic`/`webhook_id`) in the HMAC-signable content, or independently verify that the `shop` header corresponds to a shop with a real, currently valid session/installation for the delivered `topic`/`webhook_id`/`api_version` before trusting it. At minimum, document prominently that `request.shop` is unauthenticated and must be cross-checked against an existing session before being used in tenant-scoped business logic.

### Proof of Concept
```ruby
# Step 1: Attacker installs app on their own shop (attacker-shop.myshopify.com) and
# receives a genuine webhook delivery for a topic they control, e.g. products/update,
# with attacker-crafted body content:
raw_body = '{"id":1,"title":"malicious-payload"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
# Shopify computes this same value and delivers it in x-shopify-hmac-sha256 for attacker-shop.

# Step 2: Attacker replays the exact same body+hmac to the app's public webhook
# endpoint, substituting the shop-domain header for the victim shop:
forged_headers = {
  "x-shopify-topic" => "products/update",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # <-- not covered by HMAC
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds because to_signable_string only covers raw_body.
# The registered handler is invoked with data.shop == "victim-shop.myshopify.com"
# even though the payload was never produced for that shop.
```

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
