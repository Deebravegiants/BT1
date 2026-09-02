## Title
Webhook shop/topic identity is trusted from unsigned HTTP headers while HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` entirely from HTTP headers, but `to_signable_string` — the value that `Utils::HmacValidator.validate` actually verifies — is defined as only `@raw_body`. `Registry.process` trusts the header-derived `shop`/`topic` to route and label the webhook after confirming only that the *body* bytes are HMAC-valid. This breaks the identity binding: **bytes verified (the raw body) ≠ bytes acted on (headers used for shop/topic/webhook_id)**.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, none of which are part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`: [3](#0-2) 

`Registry.process` validates only that HMAC, then immediately trusts `request.shop` and `request.topic` (both header-derived, unsigned values) to select the handler and build the `WebhookMetadata` passed to application code: [4](#0-3) 

Because the shop identity is never cryptographically bound to the payload, an attacker who has captured or otherwise obtained any single valid `(raw_body, hmac-sha256)` pair that the app's own `client_secret` produced (e.g., a genuine webhook from their own store that has the app installed) can resend that exact body with the same valid HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header for an arbitrary target shop. `Registry.process` will pass HMAC validation (the body/HMAC pair is unmodified) and dispatch the handler with `WebhookMetadata.shop` set to the attacker-chosen shop string.

### Impact Explanation
This crosses a tenant boundary: the app's webhook handler is invoked believing the event pertains to shop X, when the HMAC only proves the *body* came from the app (signed with the app's `client_secret`), not that it pertains to shop X. Any handler logic keyed off `metadata.shop` (e.g. per-shop data updates, GDPR `customers/redact`/`shop/redact` processing, uninstall bookkeeping, cache invalidation) can be triggered against an arbitrary victim shop identifier chosen by the attacker. This matches the Critical "cross-tenant access" category since the gem itself fails to bind the routed tenant identifier to the cryptographic proof.

### Likelihood Explanation
The likelihood is Medium: it requires the attacker to first obtain one valid `(raw_body, hmac)` pair signed by the target app's secret. The simplest path is installing the app on the attacker's own store (many apps allow free installs / dev stores) and capturing the genuine webhook deliveries Shopify sends them, then replaying the identical body+HMAC to the app's fixed public webhook URL with a forged shop header. No access token, `client_secret`, or privileged account is required — only observation of one's own legitimately-received webhook traffic.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed content that's checked, or independently verify that the `shop-domain` header corresponds to a shop actually authorized to have triggered this specific webhook (e.g., cross-check against the session/shop associated with the given HMAC/body, or require topic-specific validation of body content against the header-provided shop). At minimum, document that `Request#shop`/`#topic` are unauthenticated header values and must not be trusted by handlers for tenant-scoping decisions unless independently corroborated.

### Proof of Concept
1. Install the target app on an attacker-controlled dev store `attacker-shop.myshopify.com`.
2. Capture a legitimate webhook delivery Shopify sends to the app's webhook endpoint, e.g.:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: customers/redact
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: abc-123

   {"customer": {...}}
   ```
3. Replay the exact same body and `X-Shopify-Hmac-Sha256` value directly to the app's webhook endpoint, but change:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) validates successfully because it only checks the unmodified body.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "customers/redact", ...)`, causing the app to process a redact/other side-effect event under the wrong shop's identity.

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
