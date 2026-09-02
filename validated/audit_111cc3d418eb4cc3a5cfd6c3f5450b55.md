## Title
Webhook `shop-domain` header not covered by HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` HTTP header — which is never part of the signed material — to determine which tenant/shop the webhook belongs to.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Webhooks::Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. only the raw body) and compares it against the HMAC: [3](#0-2) [4](#0-3) 

Once the HMAC check passes, `request.shop` is used, unverified, to build `WebhookMetadata` that is handed to the merchant's handler code as the tenant identifier: [5](#0-4) 

The binding that should hold is: `shop-domain header == shop the HMAC-signed body actually originated from`. Because the HMAC is computed only over the body, that equality is never enforced — an attacker who can produce *any* validly-signed body (using the app's `client_secret`, which is shared across every shop that installs the app) can attach an arbitrary `shop-domain` header to it.

Since Shopify webhook signing uses the app's single `client_secret` for every shop that installs the app, a merchant who legitimately installs the target app on their own store can trigger real, validly-signed webhook deliveries containing attacker-controlled data (e.g., product/order content), capture the raw body + HMAC, and replay that exact payload to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop that also has the app installed. `HmacValidator.validate` still succeeds because it never inspects the header, so the forged event is dispatched to the app's handler attributed to the victim shop.

### Impact Explanation
This breaks the tenant isolation the HMAC check is supposed to guarantee — one merchant can inject fabricated webhook events (order/customer/product data, or even mandatory GDPR topics like `customers/redact`) that the host application will process as if they originated from a different, victim shop. This is a cross-tenant access/data-integrity violation reachable by any unprivileged user who can install the app on their own shop.

### Likelihood Explanation
Any user able to install the target Shopify app on a shop they control satisfies the prerequisites — no privileged access, leaked secret, or credential theft is required. The webhook endpoint is by design internet-reachable, and headers are attacker-controlled in the replayed HTTP request.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) values in the HMAC-signed material, or otherwise cryptographically bind them to the request before trusting `request.shop`, so a signature computed for one shop/topic cannot be replayed against another. At minimum, cross-check `request.shop` against the session/shop the app expects to receive that webhook for before processing.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., `products/create`) with attacker-crafted body content; Shopify signs it with the app's shared `client_secret` and delivers it with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac>`.
3. Attacker captures the raw body and HMAC header, then POSTs the identical body + HMAC to the app's webhook endpoint, replacing only `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
4. `HmacValidator.validate` in `Webhooks::Registry.process` passes because it only checks the raw body against the HMAC (`lib/shopify_api/webhooks/request.rb:35-43`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled body content, processing it as a legitimate event for the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
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
