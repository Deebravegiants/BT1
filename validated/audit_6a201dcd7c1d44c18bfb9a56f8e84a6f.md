Based on my analysis, I found a valid analog vulnerability in the webhook processing flow, matching the "field acted on but not covered by the HMAC" pattern.

### Title
Webhook `shop-domain` header is trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values are read directly from HTTP headers that are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` then trusts `request.shop` to attribute the webhook to a specific merchant, without that binding being covered by the HMAC check.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead read directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC purely against the raw body via `Utils::HmacValidator.validate(request)`, and then constructs `WebhookMetadata` using `request.shop` — a value that was never part of the signed material: [3](#0-2) 

`HmacValidator.validate_signature` computes the digest strictly over `verifiable_query.to_signable_string` (the raw body) and compares it to the received HMAC: [4](#0-3) 

The identity binding broken here is: **the shop the HMAC authenticates (none — it authenticates only the body) versus the shop attributed to the webhook and passed to the handler (`request.shop`, from an unsigned header)**. Since the `shop-domain` header is not part of the signed content, any two values of `X-Shopify-Shop-Domain` will validate identically against the same `(raw_body, hmac)` pair.

### Impact Explanation
An attacker who legitimately installs the app on their own store (an unprivileged tenant) will receive genuinely HMAC-signed webhooks for their own shop. They can then replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. The HMAC check still passes (it only verifies the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop. This is a cross-tenant identity confusion: application logic keyed off `data.shop` (e.g., looking up the victim's session/access token to act on their store, updating victim-tenant records, or triggering side effects attributed to the wrong merchant) can be manipulated by another unprivileged merchant.

### Likelihood Explanation
Likelihood is high for any app whose webhook handlers rely on `WebhookMetadata#shop` to select the tenant context (a very common pattern, since sessions and access tokens are keyed by shop). Exploitation requires no secrets: the attacker only needs a webhook they legitimately receive for their own store and the ability to POST to the app's public webhook endpoint with modified headers — both trivially available to any unprivileged internet user who is also a merchant/tester of the app.

### Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) as part of the HMAC-verified signable content, or otherwise cryptographically bind the shop identity to the payload before it is trusted. At minimum, `Registry.process` should validate that `request.shop` matches an expected/authorized shop for the given webhook subscription rather than trusting an unsigned header verbatim.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and the valid `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker replays the identical request to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which only checks the raw body — validation succeeds.
4. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though the payload/HMAC never authenticated that shop, letting the attacker force app logic to run in the victim tenant's context. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
