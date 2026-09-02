Confirmed. The `Webhooks::Request` HMAC binds only the raw request body (`to_signable_string` returns `@raw_body`), while `topic`, `shop`, `api_version`, and `webhook_id` are read directly from HTTP headers that are never included in the signed payload. `Registry.process` forwards `request.shop` unchecked into `WebhookMetadata`, which host apps use as the authenticated tenant identifier.

### Title
Webhook `shop` (and `topic`/`webhook-id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` validates webhook authenticity via `Utils::HmacValidator.validate`, which signs/verifies only `to_signable_string` (the raw body). The `shop`, `topic`, `api_version`, and `webhook_id` values are parsed straight from HTTP headers and are never part of the signed data, yet `Registry.process` trusts `request.shop` as the authenticated tenant identity passed to the app's handler.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [1](#0-0) , and `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding [2](#0-1) . `HmacValidator.validate` computes and compares the HMAC solely against `verifiable_query.to_signable_string`, i.e. the body bytes, never the headers [3](#0-2) . `Registry.process` checks `Utils::HmacValidator.validate(request)` and then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` as if they were authenticated [4](#0-3) . Because the app's `client_secret` is shared across every shop that installs the app, a merchant who installs the app can capture a genuine, validly-signed webhook delivered to their own store, then replay the identical body/HMAC to the app's webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header for a victim shop. `HmacValidator.validate` still succeeds because the signature only covers the untouched body, breaking the identity binding `authenticated_shop == shop_used_for_tenant_data`.

### Impact Explanation
This is a cross-tenant confusion vector: an authenticated request (valid HMAC over the body) is processed under an attacker-chosen `shop` identity. Host applications that key their tenant data/session lookups off `WebhookMetadata#shop` (the gem's own documented struct field) can be made to write or process data attributed to a shop the attacker does not own, i.e. cross-tenant access driven entirely by fields the gem's own signature verification does not cover.

### Likelihood Explanation
Any merchant that installs the app can trivially obtain a validly-signed webhook payload for their own shop (webhooks are delivered to the app's public endpoint), then resend it with a modified `shop-domain` header. No access token, `client_secret`, or privileged access is required — only the ability to receive one legitimate webhook and replay it with edited headers.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed payload verification, or otherwise cryptographically bind the shop domain to the HMAC before trusting `request.shop` in `Registry.process`/`WebhookMetadata`. At minimum, document/enforce that `shop-domain` must be validated against a known, previously-authorized shop for the topic/webhook subscription before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook (e.g. `orders/create`) with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends a request to the app's webhook endpoint with the same body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged `shop` header [2](#0-1) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [5](#0-4) .
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes attacker-supplied data as belonging to the victim shop [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
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
