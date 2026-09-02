Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC over the body only, then passes `request.shop` (header-derived, unsigned) into the handler as tenant identity [3](#0-2) .

### Title
Webhook `shop-domain` header is not covered by HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The webhook authentication mechanism verifies the HMAC signature exclusively over the raw request body, while the `shop` (and `topic`/`webhook_id`) identity fields are read from HTTP headers that are entirely excluded from the signed payload. Any actor who possesses one valid `(body, hmac)` pair signed by the app's shared `client_secret` — e.g., a merchant who installed the app and receives genuine webhooks to an endpoint they control — can replay that exact `(body, hmac)` pair while substituting an arbitrary `shopify-shop-domain` header value. `ShopifyAPI::Utils::HmacValidator.validate` will report the request as authentic because it only recomputes and compares the signature over `raw_body` [4](#0-3) , and the forged `shop` value is then handed to the registered webhook handler as if it were the authenticated source shop [5](#0-4) .

### Finding Description
The identity binding that should hold is: `shop == the shop whose bytes were actually HMAC-authenticated`. In `ShopifyAPI::Webhooks::Request`:

- `hmac` is derived from the `hmac-sha256` header [6](#0-5) .
- `to_signable_string`, the only material fed into the signature check, returns solely `@raw_body` [1](#0-0) .
- `shop`, `topic`, and `webhook_id` are read directly from the `shop-domain`, `topic`, and `webhook-id` headers, none of which are part of `to_signable_string` [2](#0-1) .

`Registry.process` calls `Utils::HmacValidator.validate(request)`, which only proves that `raw_body` was signed with the app's `api_secret_key`/`client_secret` [7](#0-6) . It never proves that the `shop` header value is the one the signer intended. The validated request is then dispatched to the handler carrying the unauthenticated `request.shop` as the tenant identity: `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [5](#0-4) .

Because the `client_secret`/`api_secret_key` used for webhook HMACs is shared by the app across all of its installed shops (not shop-specific), any one merchant that has installed the app can legitimately obtain a validly-signed `(body, hmac)` pair from Shopify's real webhook delivery to their own endpoint. That merchant — an unprivileged actor with respect to any other tenant's data — can then submit the identical `(body, hmac)` pair to the app's shared webhook endpoint while setting `shopify-shop-domain` to a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks `raw_body`, so the forged request is treated as an authentic event from the victim shop.

### Impact Explanation
This breaks the shop/tenant authentication boundary that HMAC verification is supposed to enforce for webhooks. An app relying on `WebhookMetadata#shop` (i.e., `request.shop`) to select which merchant's records to create, update, or delete (a normal and encouraged usage pattern, e.g., mandatory `shop/redact` or `customers/redact` handling, or any custom topic handler) can be made to act on a different tenant's data on behalf of an attacker who does not control that tenant. This constitutes cross-tenant access/manipulation driven entirely through this gem's own webhook-verification API, without needing the app's `client_secret` or any privileged credential.

### Likelihood Explanation
Exploitation only requires: (1) being a legitimate, unprivileged merchant/installer of the target app (a normal prerequisite for interacting with any specific app's webhook stream), and (2) capturing one legitimate webhook body+hmac pair sent to the attacker's own shop (trivially done by logging the app's own webhook endpoint traffic, or by using topics with static/predictable bodies such as the mandatory `{}`-bodied compliance webhooks). No brute-forcing of the secret and no interception of another tenant's traffic is required.

### Recommendation
Include the shop domain (and ideally topic and webhook id) inside the HMAC-signed material, or otherwise cryptographically bind them to the validated body — e.g., extend `Webhooks::Request#to_signable_string` to incorporate `shop`, `topic`, and `webhook_id` (mirroring how Shopify OAuth's `AuthQuery#to_signable_string` binds `shop`, `state`, `host`, etc. into the signature at [8](#0-7) ). At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated header values and must not be trusted as tenant identifiers without additional verification (e.g., cross-checking against the shop associated with the currently active/expected session before performing tenant-scoped writes).

### Proof of Concept
1. App merchant "shop-a.myshopify.com" installs the target Shopify app and receives a legitimate webhook at the app's shared endpoint, e.g. for a mandatory topic with a static body:
   ```
   POST /webhooks
   shopify-topic: customers/data_request
   shopify-hmac-sha256: <valid-base64-hmac-of-body>
   shopify-shop-domain: shop-a.myshopify.com
   shopify-webhook-id: <id>
   Body: {}
   ```
2. Merchant A captures this exact `(body, shopify-hmac-sha256)` pair.
3. Merchant A replays it to the same shared endpoint, substituting only the shop header:
   ```
   POST /webhooks
   shopify-topic: customers/data_request
   shopify-hmac-sha256: <same-valid-base64-hmac-of-body>
   shopify-shop-domain: shop-victim.myshopify.com
   shopify-webhook-id: <id>
   Body: {}
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over the empty body and matches, per `HmacValidator.validate_signature`/`compute_signature` [9](#0-8) .
5. The handler is invoked with `WebhookMetadata#shop == "shop-victim.myshopify.com"` even though the request was crafted entirely by Merchant A, causing the app to process a compliance/data event (or any custom-topic action) against the wrong tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
