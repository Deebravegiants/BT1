Based on my analysis, the report's "identity binding broken by an unsigned field" pattern maps directly onto how this gem verifies Shopify webhooks.

### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content as only the raw request body [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by the handler are all read straight from HTTP headers that are never included in that signed string [2](#0-1) . `Registry.process` validates only the body-derived HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop_header == shop_bound_by_hmac`. Instead, `Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only `@raw_body` [1](#0-0) , and `HmacValidator` merely HMAC-compares that string against the `hmac-sha256` header using `Context.api_secret_key` [4](#0-3) . The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are parsed independently in `Request#shop`, `#topic`, `#webhook_id`, `#api_version` [2](#0-1)  and are never part of the signed payload. `Registry.process` still forwards `request.shop` straight into `WebhookMetadata` used by the app's handler after only checking the HMAC of the body [3](#0-2) .

Because the signature covers only bytes of the body, any actor who possesses one legitimately-signed `(raw_body, hmac)` pair for shop A (e.g., their own store's webhook delivery, which they can freely capture as the shop owner/admin of their own store) can replay that exact body and HMAC to the app's public webhook endpoint while substituting the `shop-domain` header for shop B. `HmacValidator.validate` still succeeds because it never inspects headers, so the forged `shop-domain` is accepted and passed to the app's handler as though it originated from shop B.

### Impact Explanation
This breaks the tenant-identity binding the gem is expected to enforce for webhook consumers: the app is told data "came from shop B" while the actual signed content was legitimately produced only for shop A. In a multi-tenant app this enables cross-tenant confusion — e.g., an attacker who owns/administers shop A can cause their own webhook payload (product/customer/order data) to be attributed to a victim shop B inside the host app, or cause replay of stale events under an arbitrary shop identity, without ever needing `api_secret_key` or a stolen access token. This matches the "Critical - cross-tenant access" impact bucket since the credential/tenant boundary (`shop`) is not actually bound by the cryptographic check that is supposed to authenticate the whole request.

### Likelihood Explanation
Exploitation only requires the ability to send an arbitrary HTTP POST to the app's public webhook endpoint plus one legitimately obtained `(body, hmac)` pair — trivially available to any merchant installed on the app, since Shopify delivers real signed webhooks to their own shop's data. No secret material, TLS interception, or privileged access is required, matching the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed material verified by `HmacValidator`, or independently authenticate that the `shop-domain` header matches a shop the app expects for that specific installation before trusting it in `WebhookMetadata`. At minimum, `Webhooks::Request#to_signable_string` should not treat header-derived identity fields as authenticated when only the body is HMAC-checked, and `Registry.process` should not forward the unauthenticated `shop` value into application-trusted metadata.

### Proof of Concept
```ruby
# Attacker owns/administers "attacker-shop.myshopify.com" and receives a legitimate webhook:
raw_body = '{"id": 123, "note": "legit order for attacker-shop"}'
legit_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(
    OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), API_SECRET_KEY, raw_body)
  ),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
}

# Attacker replays the *same* raw_body + hmac but swaps the shop header to the victim:
forged_headers = legit_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds (only raw_body is checked),
# and the handler receives WebhookMetadata with shop: "victim-shop.myshopify.com"
# even though the payload was never signed for that shop.
``` [3](#0-2)

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
