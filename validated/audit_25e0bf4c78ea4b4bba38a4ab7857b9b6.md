### Title
Webhook shop/topic identity spoofing via unsigned headers - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), event `topic`, and `webhook_id` entirely from HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies only covers the raw request body. Any user who can legitimately install the app on their own store can capture a validly-signed webhook for their own shop and replay it to the app's webhook endpoint with a forged `shop-domain` (and/or `topic`/`webhook-id`) header, causing the app to process attacker-controlled data as if it originated from an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read directly from unauthenticated HTTP headers, none of which participate in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (i.e., the body) against the secret-derived HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches based on `request.topic`, passing the unauthenticated `request.shop` straight into the handler metadata used by the host app to attribute the event to a tenant: [4](#0-3) 

Equality that should hold: `shop-identity-bound-by-signature == shop-value-acted-upon`. In this implementation that equality is false: the signature only binds `raw_body`, while `shop` (the tenant key the handler acts on) is taken from a header outside the signed scope.

### Impact Explanation
Because the HMAC secret (`client_secret`) is shared across all installations of the app, any store owner who installs the app can generate a genuinely-signed `(body, hmac)` pair for their own store (e.g. by creating an order/product with attacker-chosen field values that flow into the webhook body) and then replay that exact body+hmac to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop. The signature check still passes because the header is not part of the signed content. If the host application uses `WebhookMetadata#shop` (populated from `request.shop`) to key data or drive actions for that tenant — as the gem's own design intends — this results in cross-tenant data injection/corruption: attacker-controlled webhook content gets attributed to and processed under a victim shop's identity.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app on any Shopify store (available to any unprivileged internet user who can create a dev/trial store), and (2) the ability to trigger an event with attacker-influenced content. No access token, `client_secret`, or privileged account is required — the attacker never needs to know the shared secret, only to legitimately obtain one valid signed body from their own tenant and resend it with a different `shop-domain` header.

### Recommendation
Bind the tenant/topic identity into the signed payload validated for webhooks, e.g. by having `to_signable_string` incorporate the `shop`, `topic`, and `webhook_id` header values (in the same normalized form Shopify signs, if supported), or by requiring host applications to cross-check `request.shop` against an independently-verified installation record before trusting the payload for tenant-scoped actions. At minimum, document prominently that `shop`/`topic`/`webhook_id` are unauthenticated header values and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`.
2. Trigger a webhook event (e.g., `products/create`) with attacker-chosen field values; Shopify sends a POST to the app's webhook endpoint with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: products/create`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`.
3. Capture this valid `(body, hmac)` pair.
4. Re-POST the identical body and `X-Shopify-Hmac-Sha256` header to the same endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the body; `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) dispatches the handler with `WebhookMetadata.shop == "victim.myshopify.com"` and attacker-controlled body, causing the host app to process forged data under the victim tenant's identity.

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
