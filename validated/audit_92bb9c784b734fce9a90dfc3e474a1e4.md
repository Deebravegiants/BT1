Confirmed: the webhook HMAC only signs the raw body, while the tenant identity (`shop`) is taken from an unauthenticated header, unlike OAuth's `AuthQuery` which includes `shop` in the signed string. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook HMAC does not cover the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header, but the HMAC signature it verifies only covers the raw request body (`to_signable_string` returns `@raw_body`), not the shop header. This breaks the equality that should hold: `shop authenticated by HMAC == shop used to attribute the webhook event`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which calls `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header value. [4](#0-3) [5](#0-4) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from headers with no cryptographic binding to the signed body: [6](#0-5) 

This is inconsistent with `Auth::Oauth::AuthQuery`, where `shop` is explicitly included in `to_signable_string` and therefore covered by the HMAC: [3](#0-2) 

Because Shopify computes the webhook HMAC over the raw JSON body using the app's `client_secret`, and the same body+HMAC pair remains valid for any shop, an unprivileged attacker who owns a shop where the app is installed can capture a legitimate webhook delivery to their own endpoint (body + `hmac-sha256` header) and replay it to the app's webhook endpoint while substituting an arbitrary `shop-domain` header (or `webhook-id`/`topic`, which are also unauthenticated). `HmacValidator.validate` still passes because it never inspects the header values, only the raw body. `Registry.process` then dispatches the handler with the attacker-chosen `shop` in `WebhookMetadata`, so the app processes an event as if it originated from a shop the attacker does not control.

### Impact Explanation
This is a cross-tenant identity-binding bypass at the gem's webhook verification layer: the "shop" identity handed to app business logic is not actually verified by the HMAC. Any downstream logic (e.g., data update, redact handling, order sync) keyed off `WebhookMetadata#shop` can be triggered under a forged tenant identity by an attacker who never needs the app's `client_secret` or any privileged credential — only their own legitimate shop's webhook deliveries.

### Likelihood Explanation
Any merchant who installs the app on their own shop automatically receives genuine webhook deliveries with valid HMACs for arbitrary bodies/topics they can influence (e.g. via `metafields`, `orders`, etc.), and headers are trivially rewritable when replaying the raw HTTP request to the app's webhook endpoint, since nothing about the header values is checked against the signature. No secret material or elevated access is required beyond controlling one's own shop.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signable string used for HMAC verification (mirroring `AuthQuery#to_signable_string`), or otherwise cryptographically bind the header-derived identity fields to the signed payload, so `HmacValidator.validate` fails if any of these fields are altered independently of the body.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. by updating a product), receiving a POST with body `B`, `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays this POST to the app's webhook endpoint with the same `B` and `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers normally; `Utils::HmacValidator.validate(request)` calls `to_signable_string` (`@raw_body`, i.e. `B`) and successfully matches `H`, since headers are excluded from the signed string. [2](#0-1) 
4. `Registry.process` proceeds to invoke the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `request.shop` is `"victim-shop.myshopify.com"` despite the payload never having been signed for that shop. [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
