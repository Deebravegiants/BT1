This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . `Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)` [3](#0-2) , then passes the unauthenticated header value straight through as `WebhookMetadata#shop`, which the gem's own documentation instructs host apps to use directly as the tenant identifier for enqueuing/attributing work [4](#0-3) .

### Title
Webhook `shop` Field Not Covered by HMAC Signature Enables Tenant Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the HMAC signature only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` (tenant identity) is taken from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signed bytes.

### Finding Description
The equality the HMAC is supposed to guarantee is: `bytes_verified == bytes_acted_on`. Here, `bytes_verified` = `@raw_body` only [1](#0-0) , but `bytes_acted_on` includes the `shop` header used to build `WebhookMetadata.shop` [3](#0-2) . `HmacValidator.validate` only recomputes and compares HMAC against `verifiable_query.to_signable_string`, i.e. the body [5](#0-4) . Consequently, an attacker who has captured or can predict a `(body, hmac)` pair valid for one shop (e.g. their own installed shop, or any leaked/replayed webhook payload) can freely swap the `shop-domain` header to any other tenant's domain and the signature check still passes, since the header is never part of the signed content.

### Impact Explanation
Because the library's own documented usage pattern is `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [4](#0-3) , host apps following this guidance will attribute webhook payloads to whatever `shop` header value arrives, without any assurance that it matches the shop that actually generated (and whose secret signed) the body. This breaks the identity binding between "shop authenticated by HMAC" and "shop used for tenant-scoped processing", enabling cross-tenant data confusion/injection into another merchant's processing pipeline — matching the High-severity "cross-tenant access" impact category via a spoofed tenant identity.

### Likelihood Explanation
Exploitation requires an attacker to submit a POST directly to the app's public webhook endpoint with a `(body, hmac)` pair that is valid for their own shop (since a merchant installing the app can trigger webhooks for their own store to obtain a legitimately-signed body/hmac pair) but with the `shop-domain` header rewritten to a victim shop's domain. This requires no access to `api_secret_key` or TLS interception — only the ability to send arbitrary HTTP requests and knowledge of one legitimately-signed webhook payload for the attacker's own account.

### Recommendation
Include the `shop` (and ideally `topic`, `api-version`) header values in the signed content used for validation, or otherwise cryptographically bind the shop domain to the signature (e.g., have `HmacValidator` validate `shop-domain` header + body concatenation, matching what's actually acted upon). At minimum, document that `WebhookMetadata#shop` is not covered by the HMAC and must be independently cross-checked by host apps against known installed shops before use.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`, and the attacker triggers a real webhook event, capturing the legitimate `raw_body` and `x-shopify-hmac-sha256` value sent by Shopify to the app's webhook endpoint.
2. Attacker replays that exact `raw_body` and `hmac` to the same endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the secret [6](#0-5)  — validation succeeds because the header was never part of the signed bytes.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop = "victim-shop.myshopify.com"` [7](#0-6)  and passed to the host app's handler, which (per documented usage) processes/enqueues the attacker's payload as if it belonged to the victim shop.

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
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
