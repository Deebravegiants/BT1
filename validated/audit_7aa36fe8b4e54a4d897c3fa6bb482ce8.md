### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only, while the `shop` (tenant identity) is taken from an unauthenticated HTTP header. Any party capable of producing a body+HMAC pair (trivially possible via their own legitimate shop installation) can then replay that exact body/HMAC with a different `x-shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as a valid webhook "from" the spoofed shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value the HMAC is computed and verified over — returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it authenticates the body bytes, not the shop: [3](#0-2) 

`Registry.process` then trusts `request.shop` as the tenant identity for dispatch, forwarding it unchecked into `WebhookMetadata` and to the app-provided handler: [4](#0-3) 

This breaks the identity binding `HMAC-authenticated bytes == tenant identity acted upon`. The `shop` field is a field "acted on" by the handler (host apps key off `data.shop` to scope database writes, job enqueuing, etc., as documented) but it is not covered by the HMAC. Since a merchant/developer can freely install the app on their own store and receive a genuine, validly-signed webhook for a body of their choosing (e.g., an `orders/create` payload with attacker-chosen note/fields), they can capture a valid `(raw_body, hmac)` pair and then replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body against the secret, and `Registry.process` will hand the handler `WebhookMetadata` claiming the event is for the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who controls one tenant (their own shop/app installation) can forge webhook events attributed to a different, victim tenant, without ever possessing the app's `client_secret` or the victim's access token. Depending on how a host application uses `data.shop` (e.g., record scoping, job dispatch, cache keys, or triggering side effects tied to the shop), this enables cross-tenant data injection or state corruption — satisfying the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Any developer can create their own Shopify development store, install an app using this gem, and receive real, validly-HMAC-signed webhooks whose body content is largely under their control (order notes, custom fields, tags, etc., depending on topic). Capturing a `(body, hmac)` pair from their own store and replaying it against the target endpoint with a modified shop header requires no secrets, no privileged account, and no interception of TLS. It only requires the ability to send an HTTP request to the app's public webhook endpoint — the same endpoint Shopify itself posts to.

### Recommendation
Bind the `shop` domain into the value that is HMAC-verified, or otherwise cryptographically tie the header claim to the request's authenticity — e.g., include the shop domain in the signable string, or cross-validate `request.shop` against a shop already known/authorized for the given webhook topic/registration before dispatching to handlers. At minimum, document and enforce that host applications must not trust `data.shop` for tenant-scoping decisions without independently verifying that the shop is one for which they hold an active session/registration for that specific `webhook_id`/topic combination.

### Proof of Concept
1. Attacker installs the app on their own dev store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a body they control.
2. Attacker captures the raw POST: `raw_body` and header `x-shopify-hmac-sha256`.
3. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` builds a request object; `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the secret (`lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/request.rb#to_signable_string`).
5. `ShopifyAPI::Webhooks::Registry.process` dispatches to the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, even though this event never originated from Shopify for that shop.

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
