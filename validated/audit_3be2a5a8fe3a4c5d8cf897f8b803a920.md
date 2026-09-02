### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` attribute the app actually acts on comes from the unauthenticated `X-Shopify-Shop-Domain` header. Because the API secret used for HMAC validation is shared across every shop installed on the app (it is the app's `client_secret`, not a per-shop secret), any merchant who legitimately receives one signed webhook can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different shop's domain in the header, causing the host application to process the event as if it originated from a different tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the HMAC or against any value that is cryptographically bound to a specific shop: [2](#0-1) 

`HmacValidator.validate` verifies only the signable string (the raw body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request once the body HMAC checks out, and forwards `request.shop` — unauthenticated data — directly to the handler as the tenant identity for the event: [4](#0-3) 

The identity binding that should hold is:
`hmac(raw_body, api_secret_key) == received_hmac` should imply `shop header == the shop that Shopify actually sent this payload for`.

Because `api_secret_key` is the same value for every shop that has installed the app (it is the app's OAuth client secret, not a per-installation secret), and the shop domain is excluded from the signed payload, that implication does not hold. A user who controls a shop that has installed the app (an "unprivileged internet user" relative to other tenants of the same app) can:
1. Trigger or capture a legitimate webhook delivery for their own shop (e.g., `orders/create`), obtaining a raw body and a valid `X-Shopify-Hmac-Sha256` value signed with the app's real secret.
2. Replay that exact body and HMAC to the app's webhook endpoint, but change the `X-Shopify-Shop-Domain` header to a victim shop's domain.
3. `HmacValidator.validate` succeeds (it never looked at the shop header), so `Registry.process` proceeds and calls the topic handler with `shop: <victim shop>`.

Any host application that trusts `WebhookMetadata#shop` (as the getting-started/webhooks docs instruct apps to do) to look up the victim's stored access token/session or to perform per-tenant side effects will now execute that logic against the wrong tenant, driven entirely by attacker-controlled, unauthenticated header data.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: it allows one merchant's legitimate webhook traffic to be relayed and misattributed to a different merchant, i.e., cross-tenant access facilitated entirely from data this gem accepts as trusted after "HMAC validation." Per the rules, cross-tenant access is a Critical-impact outcome.

### Likelihood Explanation
Any developer/merchant using the shopify_api gem for their own installed app can generate at least one valid signed webhook body (this happens automatically as part of normal app usage), then replay it with a forged shop-domain header at will — no access token, secret, or privileged role is required. The only requirement is that the receiving host application trusts `shop` from `WebhookMetadata` to select the tenant context, which is exactly the documented usage pattern for this gem's webhook registry.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable string, or otherwise cryptographically bind the shop attribute to the verified payload, so that `Request#shop` cannot be varied independently of the signed body. At minimum, `Registry.process` should reject requests where the shop cannot be independently corroborated (e.g., against a per-shop secret or a previously known session for that shop) before dispatching to handlers.

### Proof of Concept
1. Configure the app with `Context.api_secret_key = "shared_secret"`.
2. As shop A (a real installed merchant), capture a real webhook delivery: `raw_body = '{"id":1}'`, `hmac = OpenSSL::HMAC.digest(SHA256, "shared_secret", raw_body)` (this is exactly what Shopify sends for shop A).
3. Send a forged request to the app's webhook endpoint with the same `raw_body` and `hmac`, but headers:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same base64 hmac captured from shop A's delivery>
   x-shopify-shop-domain: shop-b.myshopify.com   # victim shop
   ```
4. `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers))` — `HmacValidator.validate` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:12-31`, only `raw_body` is checked), and the handler is invoked with `shop: "shop-b.myshopify.com"` (per `lib/shopify_api/webhooks/registry.rb:198-199`), despite the payload never having been sent by Shopify for shop B.

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
