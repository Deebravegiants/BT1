### Title
Webhook `shop`, `topic`, and `webhook-id` header fields are trusted for tenant identification without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then hands the `shop`, `topic`, and `webhook_id` values — all taken from unauthenticated HTTP headers — directly to the app's webhook handler as the tenant identity for that payload. Because those header fields are never included in the signed data, `shop == cryptographically-authenticated shop` does not hold; only `body == cryptographically-authenticated body` holds.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors all read directly from HTTP headers, which are never part of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the raw body only) and compares it against the `hmac-sha256` header using the app's single, shared `api_secret_key`: [3](#0-2) 

`Registry.process` then trusts `request.shop` as the tenant identity and passes it straight into the handler without any additional binding check: [4](#0-3) 

Because the `api_secret_key` is shared across all shops installed on the app (it is not per-shop), any merchant who has installed the app receives legitimate webhook deliveries for their own shop, each with a valid `(raw_body, hmac)` pair signed under that shared secret. An attacker merchant can capture one of their own legitimate webhook deliveries, then replay the exact same `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and, if desired, `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because the signature check only covers `raw_body`, and `Registry.process` will invoke the handler with `shop: <victim-shop-domain>`, `body: <attacker-controlled-but-Shopify-signed JSON>`. This breaks the intended identity binding: `authenticated_body == body` but `claimed_shop != actual_source_shop`.

### Impact Explanation
This is a cross-tenant boundary violation (Critical, per the "cross-tenant access" criterion): a merchant with no privileged access to another tenant can cause the app to process attacker-supplied, Shopify-signed payload data under a victim shop's identity. Any app logic keyed off `WebhookMetadata#shop` (e.g., updating shop-scoped records, triggering shop-specific side effects, or writing/reading data associated with that shop) can be manipulated by an unrelated, unprivileged merchant.

### Likelihood Explanation
Any merchant who installs the app receives real webhook deliveries and therefore possesses at least one valid `(body, hmac)` pair signed with the app's shared secret. Replaying it with a different `shop-domain` header requires only a single unauthenticated HTTP request to the app's public webhook endpoint — no access token, session, or `client_secret` is needed.

### Recommendation
Bind the tenant-identifying headers into the signed material, or perform an independent authenticity check on `shop` before trusting it:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signed payload (not just the raw body), matching them against the values used by `Registry.process`, or
- Cross-validate the `shop` header against an independently verified source (e.g., an existing stored session/shop record) before dispatching to handlers, rejecting requests where the claimed shop cannot be corroborated.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value.
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because it only checks the body's HMAC (`lib/shopify_api/utils/hmac_validator.rb`), and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker's payload.

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
