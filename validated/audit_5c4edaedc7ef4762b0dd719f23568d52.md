### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop` header straight to the app's handler as the tenant identity, without that header ever being part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)` — i.e. HMAC(secret, raw_body) — and then dispatches `request.shop` (an unauthenticated header value) directly into `WebhookMetadata`, which is the only tenant identifier passed to the app's `WebhookHandler#handle`: [3](#0-2) [4](#0-3) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and the app's shared secret: [5](#0-4) 

This is the same bug class as the reported issue: a value that downstream code treats as an authenticated identity (`previous_sender` in the report; `shop` here) is not bound by the cryptographic check that is supposed to establish trust (`AMPCtx.origin` check in the report; the webhook HMAC here). The equality that should hold is:
`bytes verified by HMAC == bytes the tenant identity is derived from`
but in this gem: `HMAC covers raw_body only`, while `shop (tenant) is read from a separate, unsigned header`. Contrast this with the OAuth callback path, where the analogous `AuthQuery#to_signable_string` explicitly includes `shop` in the signed string: [6](#0-5) 
showing the gem's own pattern elsewhere is to bind `shop` into the signature — a pattern the webhook path does not follow.

### Impact Explanation
This is a Critical cross-tenant issue: since the HMAC key (the app's `client_secret`) is shared across every shop that installs the app, any merchant who legitimately installs the app can capture a valid `(raw_body, hmac)` pair from a real webhook delivered to their own store, and replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` (or `x-shopify-shop-domain`) header. `HmacValidator.validate` will still pass because the header is not part of `to_signable_string`, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain. Any host application that uses `data.shop` (the only tenant discriminator provided by this gem) to look up per-tenant session/access-token data or to gate per-tenant business logic will act on behalf of, or against, a shop it never actually received a webhook from — a tenant-boundary violation.

### Likelihood Explanation
Any actor able to install the app on a store they control (an "unprivileged internet user" from the app's perspective, since app installation itself requires no special privilege) can obtain a valid signed body for at least the mandatory topics (`shop/redact`, `customers/redact`, `customers/data_request`) or any subscribed topic, and replay it against the shared webhook endpoint with a forged shop header. No access token, `client_secret`, or TLS interception is required — only observation of one legitimately received webhook.

### Recommendation
Include the shop domain (and topic/webhook id, if relied upon) inside the signed material verified against the HMAC, or independently verify that the `shop` header corresponds to a shop for which the endpoint is expecting delivery (e.g., cross-check against a known/installed shop list keyed by data actually bound to the signature) before trusting it in `WebhookMetadata`. At minimum, document loudly that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook, e.g. `orders/create`, to the app's registered endpoint with headers:
   `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and body `B`.
3. Attacker captures `B` and the valid `x-shopify-hmac-sha256` value.
4. Attacker resends the same body `B` and same HMAC header to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, B)` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
6. The app's handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host application to process attacker-controlled webhook data as if it originated from the victim tenant.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
