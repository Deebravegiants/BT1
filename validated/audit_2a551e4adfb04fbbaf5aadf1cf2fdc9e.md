This confirms the finding. The `WebhookMetadata` passed to every app's `WebhookHandler#handle` carries `shop`, `topic`, `api_version`, and `webhook_id` directly from HTTP headers, none of which are covered by the HMAC signature verification in `ShopifyAPI::Webhooks::Request`.

### Title
HMAC on Webhook Requests Only Covers the Raw Body, Not the `shop`, `topic`, `api-version`, or `webhook-id` Headers Used for Tenant Identification - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` by defining `to_signable_string` as only the raw request body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read verbatim from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only this body-only HMAC before dispatching [3](#0-2) , then builds `WebhookMetadata` (including the unauthenticated `shop`) that is handed to the app's handler [4](#0-3) .

### Finding Description
The identity binding broken here is: **shop authenticated by HMAC ≠ shop delivered to the handler**. `HmacValidator.validate` calls `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to `verifiable_query.hmac` [5](#0-4) . For webhook requests, `to_signable_string` is exactly `@raw_body` — the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers are excluded from the signed content entirely [6](#0-5) .

Because the shared `api_secret_key` used for HMAC computation is the same for every shop/store that installs a given app (it is not shop-specific), any attacker who installs the app on their own shop can receive a legitimately-signed webhook (valid `raw_body` + `hmac`), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Registry.process` still calls `Utils::HmacValidator.validate(request)`, which passes because the body is unchanged and thus the signature is still valid [7](#0-6) . The resulting `WebhookMetadata.shop` — attributed to the victim tenant — is untouched by any cryptographic check [8](#0-7) .

### Impact Explanation
This is a cross-tenant identity confusion at the library level: the gem's own webhook-processing pipeline hands the app's `WebhookHandler#handle` a `shop` value that was never covered by the HMAC it just validated. Any host application that (reasonably, given the API contract) trusts `WebhookMetadata#shop` for tenant routing/persistence can have webhook data attributed to, or acted upon under, the wrong merchant's tenant — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only an unprivileged action: installing the app on an attacker-controlled shop (a normal, permitted operation for any Shopify developer/merchant) to obtain one legitimately HMAC-signed body, then replaying it with a forged shop header value. No `api_secret_key`, access token, or victim credentials are needed.

### Recommendation
Include the `shop`/tenant-identifying header (and ideally `topic`, `webhook_id`, `api_version`) inside the HMAC-signed material for webhook requests, or otherwise cryptographically bind the shop domain to the signed payload before constructing `WebhookMetadata`, so `HmacValidator.validate` cannot pass while the delivered `shop` value is unauthenticated.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a genuine webhook POST, including `raw_body` and the valid `x-shopify-hmac-sha256` value computed by Shopify with the app's `client_secret`.
2. Resend the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) ; since `to_signable_string` is only `raw_body`, the signature check passes.
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` [8](#0-7) , causing the app to process/store attacker-supplied data under the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
