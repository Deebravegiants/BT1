### Title
Webhook `shop` (and `topic`/`webhook-id`) Headers Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the tenant-identifying `shop-domain` header (and `topic`/`webhook-id`) are read straight from unauthenticated HTTP headers. `Registry.process` verifies only the body HMAC and then forwards this unauthenticated `shop` value to the app's webhook handler as the trusted tenant identifier, breaking the equality `shop verified-by-HMAC == shop used for tenant routing`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read from HTTP headers that are never included in the signed string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. the raw body, with no binding to `shop`: [3](#0-2) 

`Registry.process` validates HMAC and then immediately trusts `request.shop` as the tenant to pass into the handler, with no cross-check against any expected/registered shop: [4](#0-3) 

Because the `api_secret_key` used to compute the webhook HMAC is the single app-level secret (shared across every shop that installs the app, not per-tenant), any tenant that installs the app can legitimately trigger a webhook whose body they substantially control (e.g. by naming a product/order field with attacker-chosen JSON-safe content) and thereby obtain a valid `(raw_body, hmac)` pair signed with the app's secret. Since the `shop-domain` header is not part of the signed content, that exact `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with an arbitrary, attacker-chosen `x-shopify-shop-domain` header — including the domain of a completely different shop the attacker never installed the app on. `Registry.process` will accept the HMAC and hand the handler a `WebhookMetadata` tagged with the spoofed shop: [5](#0-4) 

This is a direct instance of "a field acted on but not covered by the HMAC" — the shop identity used downstream (for tenant-scoped data writes, session lookups keyed by shop, etc.) is never bound to the cryptographic signature that is supposed to authenticate the request as originating from Shopify for that shop.

### Impact Explanation
This is a Critical cross-tenant issue: an unprivileged app installer (any shop owner who installs the target app) can forge webhook events that the app attributes to an arbitrary other tenant shop, without needing that victim shop's credentials, access token, or `client_secret`. Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g. to look up/update per-shop records, credit actions, or trigger merchant-facing side effects), this can lead to cross-tenant data corruption or spoofed events being recorded against a victim merchant's account.

### Likelihood Explanation
Any legitimate (even free/trial) installer of the app can trigger events (e.g., `products/create`, `orders/create`) in their own store to obtain a validly-HMAC-signed body, and needs only to replay that request with a modified `x-shopify-shop-domain` (or `shopify-shop-domain`) header to a public webhook endpoint URL that the app itself has registered and exposed. No secret material or privileged access is required beyond running a normal, unprivileged store installation.

### Recommendation
Bind the trusted tenant identity to the signed content, or at minimum sign the header set together with the body: compute the webhook HMAC over a canonical string that includes `shop-domain`, `topic`, and `webhook-id` in addition to the raw body, and reject requests where these fields aren't covered. If Shopify's wire protocol prevents changing what is signed, mitigate by treating `request.shop` as an untrusted hint and revalidating it against a session/store record obtained from the app's own persisted, credential-derived data (e.g. cross-check with a shop this app instance is actually authorized against) before using it for any tenant-scoped operation.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and triggers `products/create` with a crafted title/body such that the resulting webhook payload (`raw_body`) is fully known to them.
2. The app's endpoint receives the legitimate webhook: headers include `x-shopify-hmac-sha256: <valid-hmac-of-raw_body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `raw_body` and the valid `hmac` value (their own traffic to their own endpoint).
4. Attacker resends the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully (`Request#shop` returns `"victim-shop.myshopify.com"`), `HmacValidator.validate` succeeds because it only checks the body-derived HMAC, and `Registry.process` invokes the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to process attacker-controlled data as if it came from the victim shop. [5](#0-4) [6](#0-5)

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
