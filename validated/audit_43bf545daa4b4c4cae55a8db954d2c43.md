Confirmed: `WebhookMetadata.shop` at [1](#0-0)  is populated directly from `request.shop`, which is passed unauthenticated into the handler by `Registry.process`.

### Title
Webhook `shop-domain` header is trusted without HMAC coverage, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the HMAC signature over the raw request body only, while the `shop-domain` header — the value the host application uses to attribute the webhook to a specific merchant/tenant — is read separately and is never included in the signed material. Any party that can obtain one genuinely-signed webhook body/HMAC pair (e.g., the owner of any shop that has installed the app) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the library will report the webhook as valid and pass the attacker-chosen shop identity to the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [2](#0-1)  and `Request#shop` is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [3](#0-2) . `Utils::HmacValidator.validate` verifies the HMAC strictly against `verifiable_query.to_signable_string`, i.e., the body, using `OpenSSL.secure_compare`: [4](#0-3) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` and then forwards `request.shop` straight into `WebhookMetadata`, which is delivered to the app's handler as the tenant identity: [5](#0-4) .

This breaks the intended identity binding: `hmac_valid(body) == true` is treated as proof that `(body, shop)` both originated from Shopify for that specific shop, but the equality that is actually checked is only `hmac_valid(body)`; `shop` is unauthenticated attacker-controlled input carried alongside a validly-signed body.

### Impact Explanation
Because the shop attribution is not cryptographically bound to the signed payload, an attacker who legitimately installs the target app on their own store (an unprivileged internet user with no special access) receives genuine webhooks addressed to their own shop, signed with the app's real secret. They can then replay the identical raw body and HMAC value to the same public webhook endpoint while swapping the `X-Shopify-Shop-Domain` header for a victim shop domain. `Registry.process` will accept the HMAC as valid and hand the handler a `WebhookMetadata` claiming the event/body belongs to the victim shop. Any host application that uses `WebhookMetadata#shop` to select which tenant's records to create/update/delete (the documented purpose of the field) can be made to write or act on data under a shop it does not control — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
Any user capable of installing the app on a store they control (i.e., any merchant, requiring no privileged access, leaked secrets, or social engineering) can obtain a validly signed webhook body/HMAC pair and replay it with a forged shop header directly against the app's public webhook endpoint. No knowledge of `api_secret_key` is required since the attacker reuses a genuine, previously-issued signature.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind the shop identity to the signed payload before it is trusted; alternatively, cross-check the `shop-domain` header against the shop associated with the session/install record independently of the raw-body HMAC before dispatching to `WebhookHandler#handle`.

### Proof of Concept
1. Install the target Shopify app on attacker-owned store `attacker.myshopify.com`.
2. Trigger any webhook topic the app subscribes to; capture the raw POST body and its `X-Shopify-Hmac-Sha256` header sent by Shopify (both are legitimately signed with the app's real secret for this exact body).
3. Replay an HTTP POST to the app's public webhook endpoint with the same body and same `X-Shopify-Hmac-Sha256` header, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks the body against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`), and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) forwards `shop: "victim.myshopify.com"` to the app's handler, causing it to act as though the event originated from the victim's shop.

### Citations

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
