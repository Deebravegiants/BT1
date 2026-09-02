### Title
Webhook HMAC Does Not Cover `shop`/`topic`/`webhook_id` Headers, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively against that raw body. The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers that are never included in the signed payload, so an attacker who possesses one validly-signed webhook body can forge those header fields to point at a different shop or topic while keeping the same, still-valid HMAC.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and compares it with `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are extracted from HTTP headers that are outside the signed content: [2](#0-1) 

`Registry.process` gates only on this body-only HMAC check, then forwards `request.shop` and `request.topic` straight to the app's handler without any additional binding: [3](#0-2) 

The identity binding that should hold is:
`hmac_verified(body) == (shop, topic, webhook_id)_trusted`

but the implementation only proves `hmac_verified(body)`, while `(shop, topic, webhook_id)` are taken from unauthenticated header bytes. Since the `api_secret_key` is shared by the app across all shops that install it (not shop-specific), any party that obtains one validly-signed webhook body/HMAC pair for shop A (e.g., a malicious merchant who installs the app and receives a webhook for their own store) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for shop B. `HmacValidator.validate` still returns `true` (the body-derived signature is unchanged), and `Registry.process` will invoke the handler with `WebhookMetadata.shop == "shop-B"` even though the payload was never actually sent, or signed, for shop B.

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC check is supposed to provide: a single validly-signed body can be relabeled to any target shop domain or topic. Depending on how the host app uses `WebhookMetadata#shop`/`#topic` (e.g., to select which merchant's data record to update, delete, or overwrite based on webhook content), this enables cross-tenant data corruption/access using data nominally belonging to one merchant but attributed to another — a cross-tenant access violation stemming purely from a gap in this gem's own signature-verification contract.

### Likelihood Explanation
Requires the attacker to have legitimately received (or otherwise obtained) at least one genuine webhook body+HMAC pair signed with the app's `api_secret_key` — which is realistic for any merchant who installs the app (they will receive normal webhooks for their own store) and then replays that captured payload with a modified `shopify-shop-domain`/`shopify-topic` header toward the app's public webhook endpoint. No access to the `api_secret_key` itself, TLS interception, or privileged account is needed.

### Recommendation
Include the identity fields (`shop`, `topic`, `webhook_id`) in the signed payload compared by `to_signable_string`, or independently verify that the `shop` header corresponds to a shop the app expects for that specific webhook subscription before dispatching to the handler, so the HMAC binds body and header identity together.

### Proof of Concept
1. App merchant "shop-a.myshopify.com" installs the app and receives a legitimate webhook: headers `{shopify-shop-domain: shop-a.myshopify.com, shopify-topic: orders/create, shopify-hmac-sha256: <valid-hmac-of-body>}` with body `B`.
2. Attacker (the same merchant, or anyone who captured this request) resends it to the app's webhook endpoint with header `shopify-shop-domain` changed to `shop-b.myshopify.com`, keeping body `B` and the original `shopify-hmac-sha256` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) only — this still matches, so validation passes: [3](#0-2) 
4. The handler is invoked with `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)`, i.e., body `B` (data belonging to shop A) is processed as if it came from shop B.

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
