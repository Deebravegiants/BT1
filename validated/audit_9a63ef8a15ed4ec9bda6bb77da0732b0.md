## Title
Webhook `shop` identity is not covered by the HMAC signature, allowing shop-domain spoofing in webhook dispatch - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, but the `shop` value that is handed to the app's webhook handler is read from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, which is never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, not the shop-domain header: [1](#0-0) 

`HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e., `@raw_body`) and compares it against the `hmac` value (itself parsed from the `hmac-sha256` header): [2](#0-1) 

`Registry.process` then validates the HMAC and, upon success, dispatches to the handler using `request.shop`, which is taken straight from the `shop-domain` header without any cross-check against the HMAC-covered content: [3](#0-2) 

The identity binding the gem is implicitly supposed to guarantee is: `shop reported to the handler == shop whose secret produced this signed request`. In reality the code only proves `raw_body == HMAC(raw_body, secret)`; the `shop` header is fully attacker-controlled and unauthenticated. Any party that can obtain one valid `(raw_body, hmac)` pair for a given app — which any merchant who installs the app on their own store can trivially obtain by triggering a webhook — can replay that exact body/HMAC pair while substituting an arbitrary value in `X-Shopify-Shop-Domain`. The forged request will pass `Utils::HmacValidator.validate` unchanged, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain.

### Impact Explanation
Any app that uses `WebhookMetadata#shop` to key per-tenant data (look up a session/access token for that shop, write to a per-shop record, trigger a tenant-scoped action, etc.) is exposed to cross-tenant data confusion: an attacker who legitimately installed the app on shop A can cause the handler to believe the event belongs to shop B, forging events for a shop they do not control. This is a cross-tenant identity-binding break carried entirely through this gem's webhook verification path, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Likelihood is high for any consumer relying on the documented API as intended: obtaining a valid `(body, hmac)` pair requires no privileged credentials — just installing the app (or triggering any webhook topic) on an attacker-controlled store, which is normal unprivileged usage. Replaying that captured body with a modified shop-domain header is trivial and requires no knowledge of `api_secret_key`.

### Recommendation
Include the shop domain (and topic/webhook-id, if used for dispatch decisions) in the HMAC-covered signable content, or otherwise cryptographically bind the `shop` value to the verified body before it is handed to `handler.handle`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be cross-validated by the host application against a known, previously-installed shop record before being trusted for tenant-scoped operations.

### Proof of Concept
1. Install the demo/target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) and capture the raw POST body `B` plus its `X-Shopify-Hmac-Sha256` header value `H` (valid because it was signed for `B` with the app's real secret).
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` only look at the body, so `Utils::HmacValidator.validate` returns `true`.
4. `ShopifyAPI::Webhooks::Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)`, even though the payload actually originated from, and was signed for, `attacker.myshopify.com`.

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
