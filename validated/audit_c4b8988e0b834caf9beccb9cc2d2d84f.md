### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers (`x-shopify-shop-domain`, etc.) with no cryptographic binding to those values [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC matches `verifiable_query.to_signable_string`, i.e. the body [3](#0-2) . `Webhooks::Registry.process` accepts the request once this body-only HMAC passes, and then dispatches to the handler using the unauthenticated `request.shop` value taken straight from the header [4](#0-3) .

This breaks the intended identity binding: `shop_the_app_believes_sent_this_webhook == shop_that_actually_produced_the_HMAC`. Since the app's `api_secret_key` is shared across every shop that installs the app (not shop-specific), any shop that has the app installed can receive a legitimately Shopify-signed webhook (valid HMAC over a given body) for its own store, then replay that exact `raw_body`/`hmac` pair while substituting the `x-shopify-shop-domain` header for a different, victim shop that also has the app installed. Because the signature only covers the body, this forged request passes `HmacValidator.validate` and is processed by the handler as if it came from the victim shop — a cross-tenant identity confusion inside the gem's own webhook verification path.

### Impact Explanation
This is a cross-tenant identity-binding failure inside the gem's webhook verification logic (`Webhooks::Request`/`Webhooks::Registry`/`Utils::HmacValidator`), which host applications rely on to trust `WebhookMetadata#shop`. An attacker who legitimately installs the target app on their own store (a normal, unprivileged action available to anyone) can obtain valid signed webhook bodies and then attribute that data to any other shop domain of their choosing, without ever needing the app's `api_secret_key`, an access token, or any privileged credential. Depending on how the host app uses `WebhookMetadata.shop` (e.g., looking up sessions/tenant data, triggering data mutations scoped by shop), this can be leveraged for cross-tenant data corruption or disclosure.

### Likelihood Explanation
Any developer/attacker can install the target app on a store they control (dev store or their own paid store) and receive genuine Shopify webhooks with valid HMACs. Replaying the exact `raw_body` while forging the `x-shopify-shop-domain` header requires no cryptographic secret and no special network position — a standard HTTP client suffices, since the header is not covered by the signature at all.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signed material, or otherwise cryptographically bind the `shop-domain` header to the verified body (e.g., verify shop against a per-installation secret/session record rather than trusting the header), so that a valid HMAC for one shop's payload cannot be replayed under another shop's identity.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled Shop A. Shopify sends a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (HMAC of `B` with the app's shared `api_secret_key`), and `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker captures `B` and `H`.
3. Attacker crafts a new POST to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (a different shop that also has the app installed).
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only (via `Webhooks::Request#to_signable_string`), which matches `H`, so verification succeeds [5](#0-4) .
5. `Webhooks::Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [6](#0-5) , causing the host app to process Shop A's webhook data as though it belongs to `victim-shop`.

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
