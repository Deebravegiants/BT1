## Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling shop-identity spoofing on otherwise-valid webhook deliveries - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC signature computed over the raw request body, but the `shop` value handed to the app's handler is read from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is never included in the signed payload. This breaks the binding `shop authenticated via HMAC == shop attributed to the processed data`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived purely from a header that is not part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC strictly over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` performs this HMAC check, then immediately forwards `request.shop` (the unauthenticated header value) to the app's handler as the tenant identity, with no cross-check that the header-derived shop matches anything cryptographically bound to the request: [4](#0-3) 

Because the HMAC only binds `secret + raw_body`, any request whose body+HMAC pair is valid (e.g., a webhook payload delivered to the attacker's own installed app instance, or any body the attacker can get validly signed for their own shop) remains HMAC-valid if the `x-shopify-shop-domain` header is swapped for a different (victim) shop domain. The gem's own verification logic has no mechanism to detect this tampering, since the shop identity is never part of the signed content.

### Impact Explanation
This crosses a tenant boundary: an unprivileged user who controls or receives webhooks for shop A (e.g., by installing the app on their own store) can replay the same HTTP body/HMAC pair while substituting shop B's domain in the `shop-domain` header. The app's webhook handler — which trusts `WebhookMetadata.shop` from this gem to select per-tenant state, credentials, or database records — will process/act on the payload as if it originated from shop B, resulting in cross-tenant data confusion/injection under the identity of a shop the attacker does not control. This matches the "Critical - cross-tenant access" impact criteria.

### Likelihood Explanation
Likelihood is moderate: the attacker needs a validly-HMAC-signed body (trivially obtainable by installing the app on a shop they control and capturing the real webhook delivery), and simply needs to resend it with a different `shop-domain` header value to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged access is required — only the ability to observe one legitimate webhook from Shopify to their own store and replay it with a modified header, which is exactly the "unprivileged internet user" threat model in scope.

### Recommendation
Include the shop domain (and ideally the webhook id / topic) inside the HMAC-signed content, or otherwise cryptographically bind the `shop-domain` header to the verified payload before it is exposed via `WebhookMetadata`. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should compute the signable string over `shop + topic + raw_body` (or equivalent) rather than `raw_body` alone, so that tampering with the shop header invalidates the HMAC.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook delivery, including its raw body and valid `x-shopify-hmac-sha256` header (computed by Shopify using the app's real `api_secret_key`, unknown to the attacker but already applied to this body).
2. Resend the exact same raw body and HMAC header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the secret — unaffected by the header change: [3](#0-2) 
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now returns `"victim-shop.myshopify.com"`: [5](#0-4) 
5. The app processes the payload as belonging to `victim-shop.myshopify.com`, even though it was never sent by or for that shop.

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
