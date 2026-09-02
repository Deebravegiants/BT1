## Title
Webhook `shop-domain` header is trusted for tenant identification while the HMAC signature only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, but the signable string used for that HMAC is only the raw request body, not the `shop-domain` header. Because the tenant identity (`shop`) is read straight from an unauthenticated, unsigned header and handed to the webhook handler, the binding "HMAC-verified bytes == bytes the handler trusts as the tenant identity" is broken.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC only against `to_signable_string` (i.e. the body): [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then forwards `request.shop` (the unsigned header) straight to the handler as the tenant identifier, with no cross-check against any signed field: [4](#0-3) 

Because `shop` never enters the signed material, any party who can obtain one genuine, validly-signed webhook body+HMAC pair for a shop they legitimately control (e.g., by installing the app on their own store and triggering a webhook topic) can replay that exact `(raw_body, hmac)` pair while substituting an arbitrary victim `shop-domain` header. The HMAC check still passes — it only ever validated the body — yet `WebhookMetadata.shop` now reports the victim's shop to the handler. This is precisely the "field acted on but not covered by the HMAC" identity-binding failure: the equality the code implicitly assumes, `verified(shop) == used(shop)`, does not hold; only `verified(body) == used(body)` is actually enforced.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` to select which merchant's session/access token/data to update — the standard pattern shown in this gem's own docs (`register` webhooks "for a shop" and process them per-shop) — can be tricked into attributing an attacker-supplied, attacker-controlled webhook body to a different, victim shop. Since access-token lookup, data writes, and business logic are commonly keyed off this `shop` value, this enables cross-tenant data confusion/injection: an attacker-controlled payload processed under a victim shop's identity. This falls under Critical - cross-tenant access.

### Likelihood Explanation
The attacker only needs to be an app-installing merchant on their own store (an unprivileged action available to any internet user who installs a public/dev app) to obtain a real `(body, hmac)` pair for a topic of their choosing; they never need the app's `client_secret` or another shop's credentials. Swapping one HTTP header is trivial. Likelihood is High for any consumer relying on `request.shop`/`WebhookMetadata.shop` as a trusted tenant key without additional verification.

### Recommendation
Bind the shop identity into the verified material: either include `shop-domain` (and ideally `topic`, `webhook-id`) in the HMAC-signable string, or independently verify that the shop asserted in the header actually owns a currently-registered subscription/session before trusting it, rather than passing the raw header value through unchecked in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and registers a webhook for topic `orders/create` (legitimate self-install).
2. Attacker triggers the webhook by placing an order (or by controlling the exact body they want processed), receiving a genuine request:
   - headers: `shopify-hmac-sha256: <valid HMAC over body>`, `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`
   - body: attacker-crafted JSON payload.
3. Attacker replays the identical `raw_body` and `hmac` header to the app's webhook endpoint but changes only `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks the body against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:198-199`) invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker's body, even though that body never originated from, nor was authorized by, the victim shop.

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
