Based on my investigation, I found a concrete analog in the webhook processing path.

### Title
Webhook HMAC covers only the request body, allowing `shop-domain` and `topic` header spoofing across tenants - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers. Any party capable of producing one valid `(body, hmac)` pair for the shared app secret (e.g., a merchant who installs the app on their own shop and receives genuine webhooks) can replay that exact body/HMAC pair while substituting the `shopify-shop-domain` and `shopify-topic` headers for another tenant. The signature check still passes because those headers are never part of the signed content, letting an unprivileged installer inject webhook events attributed to a victim shop.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, using the shared `Context.api_secret_key`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw body, and `hmac` is derived from the `hmac-sha256` header. But `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from other, unsigned headers: [2](#0-1) 

`Registry.process` only checks the HMAC of the body, then dispatches the handler using the unauthenticated `shop`/`topic` header values: [3](#0-2) 

The identity binding that should hold is: **`hmac` == HMAC(secret, body ∥ shop ∥ topic)`**, i.e., the shop/topic that determines tenant routing must be covered by the same signature that authenticates the payload. Instead the actual binding enforced is only **`hmac == HMAC(secret, body)`**, with `shop`/`topic` supplied out-of-band via headers that are never mixed into the signed string. Since the app's `client_secret` (and therefore the webhook HMAC secret) is shared across all shops that install the app — not shop-specific — any installer who receives one genuine webhook for their own store can capture a valid `(body, hmac)` pair and resend it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop and/or `shopify-topic` changed to a different event type. `Registry.process` will accept the forged headers because the HMAC only proves the body was signed by the app's secret — not which shop or topic it belongs to.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): a low-privilege actor who merely installs the app on a store they control can forge webhook events that the host application will process as if they originated from an arbitrary victim shop, with attacker-chosen topic and attacker-influenced body content (since they generate the original genuine webhook by taking actions on their own store, e.g., updating a product to control the JSON body). Depending on how the host app's `WebhookHandler#handle` implementations act on `data.shop` and `data.body` (e.g., updating per-shop records, granting access, syncing data), this can lead to unauthorized cross-tenant data manipulation or disclosure.

### Likelihood Explanation
Requires only an unprivileged app installation (something any user can do for a public/embedded app) and the ability to send an arbitrary HTTP request to the app's webhook endpoint with attacker-controlled headers and a captured, genuinely-signed body. No access to the `api_secret_key` or any victim credentials is needed.

### Recommendation
Include the tenant-identifying and event-identifying fields (`shop-domain`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signed content, or otherwise cryptographically bind them to the body (e.g., by signing a canonicalized string containing headers + body) so header values cannot be swapped independently of a valid signature. At minimum, the `Registry.process` should not trust `request.shop`/`request.topic` for anything security-sensitive unless those values are covered by the verified signature.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `products/update`) by modifying a product so the JSON body content is attacker-chosen.
2. Shopify sends the app a genuine webhook request with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: products/update`, `shopify-hmac-sha256: <valid HMAC of body>`.
3. Attacker captures this request, then resends it directly to the app's webhook endpoint with `shopify-shop-domain` changed to `victim.myshopify.com` (and/or `shopify-topic` changed to a registered mandatory topic like `customers/data_request`), keeping the same body and `hmac-sha256` header unchanged.
4. `HmacValidator.validate` in `Registry.process` [4](#0-3)  succeeds because it only checks the body's signature, and the handler is invoked with `WebhookMetadata.new(topic: "customers/data_request", shop: "victim.myshopify.com", body: <attacker body>, ...)` [5](#0-4) , causing the host app to act on forged cross-tenant webhook data.

### Citations

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
