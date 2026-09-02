## Finding: Webhook HMAC only covers the request body — `shop`, `topic`, and other identity headers are unauthenticated

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers that are never included in the HMAC computation. `Registry.process` trusts these header values once the body-only HMAC passes, so any actor who can obtain one legitimately-signed `(body, hmac)` pair for the shared app secret can replay it with arbitrary `shop`/`topic` headers and have it accepted as an authentic webhook for a different tenant.

### Finding Description
The binding that should hold is:
`HMAC-verified bytes == bytes the handler trusts for identity (shop, topic, webhook_id, api_version)`

but in this gem it is actually:

`HMAC-verified bytes == raw_body only` [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are pulled directly from (attacker-controllable-at-the-transport-layer) headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC of the request, then dispatches based on the unauthenticated `topic`/`shop` values: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it has no knowledge of, or binding to, shop/topic: [4](#0-3) 

Because the same `api_secret_key` is shared across every shop that installs a given app, any merchant who installs the app receives genuinely-signed `(raw_body, hmac)` pairs for their own shop's webhook traffic. Since `shop` and `topic` are excluded from the signed content, that same `(raw_body, hmac)` pair remains valid when replayed to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (a different, victim shop that also has the app installed) and/or a forged `X-Shopify-Topic` header. `Registry.process` will accept it as an authentic webhook and hand the attacker-chosen `shop` value straight to the handler.

### Impact Explanation
This breaks the tenant-isolation guarantee webhook consumers rely on: handlers are written assuming `WebhookMetadata#shop` is the shop that Shopify actually attests to via the HMAC. An attacker who is themselves an installer of the app (i.e., an "unprivileged" merchant relative to other tenants) can:
- Forge webhook deliveries that appear to originate from any other shop running the same app (cross-tenant), potentially triggering shop-scoped side effects (e.g., data resync, entitlement changes, uninstall/GDPR handling) keyed off `request.shop`.
- Relabel the `topic` of a captured payload to route it to a different handler than Shopify actually intended.

This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is realistic: any attacker can install the target app on their own store (a normal, unprivileged action) and thereby obtain authentic `(body, hmac)` pairs for a fixed, shared `api_secret_key`. No access token, leaked credential, or privileged account is required — only the ability to receive at least one webhook for the shared app and then send arbitrary HTTP requests to the app's public webhook endpoint with modified headers.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook_id`/`api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed payload, so that `HmacValidator.validate` fails if any of these headers are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, and receives a legitimate webhook delivery, e.g. `orders/create`, with raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid since `H = HMAC(secret, B)`).
2. Attacker sends a POST to the app's public webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <any registered topic>`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this passes because `B` and `H` are unchanged.
4. The handler is invoked with `WebhookMetadata.new(topic: "<attacker-chosen>", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the app processes attacker-controlled data as if it were an authentic event for `victim-shop.myshopify.com`. [3](#0-2) [5](#0-4)

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
