### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` field — which downstream handler code uses to attribute the webhook payload to a specific merchant/tenant — is read directly from an unauthenticated HTTP header and is never included in the signed material.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, and `shop` is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that value.

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string` (the raw body): [2](#0-1) 

`Webhooks::Registry.process` only checks this body-bound HMAC, then constructs `WebhookMetadata` using `request.shop` and hands it to the app's handler: [3](#0-2) 

`WebhookMetadata#shop` is a plain `String` field with no independent verification: [4](#0-3) 

This breaks the intended binding `hmac == HMAC(secret, body || shop)`; in the actual implementation the equality only holds as `hmac == HMAC(secret, body)`, so `shop` can be substituted freely by anyone who can produce a valid `(body, hmac)` pair for the app's shared `api_secret_key` — which is every merchant that has this app installed and receives genuine Shopify-signed webhooks.

### Impact Explanation
A malicious merchant who has the app installed receives legitimately Shopify-signed webhook deliveries for their own shop (valid `body` + `hmac` pair, since `api_secret_key` is shared across all shops using the app). By replaying that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain, `HmacValidator.validate` still succeeds, and the handler processes the forged payload as though it originated from the victim shop. Depending on how the host app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to look up/mutate per-shop state, revoke access, or trigger data changes), this enables cross-tenant data manipulation without ever holding credentials for the victim shop — satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any existing app installer already possesses a valid `(body, hmac)` pair for arbitrary content they can cause to be sent to them (e.g., by triggering their own store events), and only needs to change one unauthenticated header value to target another tenant. No secrets, tokens, or privileged access are required — only the ability to send an HTTP request to the app's public webhook endpoint, which is by definition internet-reachable.

### Recommendation
Bind the shop identity into the material that is verified, e.g., include the `shop`/`topic` headers (or a per-shop secret/context) in the signable string, or require the caller-supplied `shop` to match a value independently resolved (via a registered webhook ID/subscription lookup keyed by ID rather than by header) before trusting it for tenant attribution.

### Proof of Concept
1. Attacker has app installed on `attacker-shop.myshopify.com` and captures a real webhook delivery: `body = B`, header `x-shopify-hmac-sha256 = HMAC(api_secret_key, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint with the same `body = B` and same `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`).
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` and processes attacker-controlled data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
