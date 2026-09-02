Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop` is read straight from the `shop-domain` HTTP header (`lib/shopify_api/webhooks/request.rb:20-23`) and `Registry.process` validates the HMAC and then dispatches to the handler using `request.shop` without any cross-check between the header and the signed body [1](#0-0) .

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing on valid webhook deliveries - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, but the `shop` (and `topic`/`api_version`/`webhook_id`) values consumed by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers. This is the same class of bug as the reported `ShortLongSpell#openPosition` issue: the code verifies one piece of data (the body, via HMAC) but acts on a different, unverified piece of data (the `shop-domain` header) as if it had been authenticated together with it.

### Finding Description
`Utils::VerifiableQuery#to_signable_string` is the only content covered by `Utils::HmacValidator.validate` [2](#0-1) . For webhook requests, `Request#to_signable_string` returns `@raw_body` exclusively [3](#0-2) , while `Request#shop` is pulled directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that body [4](#0-3) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., "is this body correctly signed by *some* shop using the app's secret") and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the merchant's handler: [1](#0-0) 

The identity binding that should hold is: `shop_that_signed_the_body == shop_used_by_the_handler`. Because `shop-domain` is not part of the signed content, this equality is never checked — the HMAC only proves the app's secret was used to sign *the body bytes*, not that a particular shop sent it.

### Impact Explanation
Since HMAC validity only requires knowledge of the app's `client_secret` (which the host application already possesses and uses to receive legitimate webhooks from Shopify for any shop installed on the app), any legitimately-signed webhook payload for Shop A can be replayed with the `shop-domain` header rewritten to Shop B. `Registry.process` will pass HMAC validation (body unchanged) and hand the handler a `WebhookMetadata` claiming the data belongs to Shop B, when it was actually signed for Shop A. Depending on how the host app's webhook handler uses `data.shop` (e.g., to look up the merchant's session/access token or to write tenant-scoped data), this breaks cross-tenant isolation — an attacker controlling or observing webhook traffic for their own shop can inject data attributed to a victim shop into the host application, i.e., cross-tenant access.

### Likelihood Explanation
Exploitation requires the attacker to be able to deliver an HTTP request to the host application's webhook endpoint with a header they control (`shop-domain`) alongside a body/HMAC pair that is valid for *some* shop under the app (e.g., their own installed shop, from which they can capture a real webhook delivery and replay it with a modified header). This does not require the app's `client_secret`, an access token, or any privileged credential — only the ability to receive one legitimate webhook for their own tenant and replay it with a modified header, which is within reach of an "unprivileged" app-installing user.

### Recommendation
Bind `shop-domain` (and ideally `topic`, `api_version`, `webhook_id`) into the signed content checked by `HmacValidator`, e.g., by including the relevant headers in `to_signable_string`, or by having `Registry.process` independently verify that the shop header matches shop information embedded in the verified body/topic before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and captures a legitimately delivered webhook: headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-for-body>`, plus body `B`.
2. Attacker resends the identical body `B` and HMAC to the app's webhook endpoint but rewrites the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against the HMAC [5](#0-4) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: parsed_body, ...)` [6](#0-5) , even though the payload was never actually signed/sent for `victim.myshopify.com`.

### Citations

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
