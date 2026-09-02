### Title
Webhook `shop-domain` header is trusted by `Registry.process` without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, so `Utils::HmacValidator.validate` verifies the HMAC solely over `@raw_body`. The `x-shopify-shop-domain` / `shopify-shop-domain` header is parsed by `Request#shop` and handed to the host app's webhook handler as the trusted tenant identifier, but that header is never part of the signed material. Any request whose body still produces a valid HMAC (i.e., a body the attacker previously received a genuine, correctly-signed webhook for) can be replayed with an arbitrary `shop-domain` header value, and the library will accept it as authentic for that arbitrary shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and the HMAC check in `HmacValidator.validate_signature` computes the signature only from `to_signable_string`: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (parsed from the `shop-domain` header) as the tenant identity forwarded to the app's handler: [3](#0-2) 

`Request#shop` is read straight from an HTTP header with no cryptographic binding to the signed body: [4](#0-3) 

The identity binding this breaks, stated as an equality that should hold but does not:
`shop_in_signed_material == shop_delivered_to_handler`
In this library, `shop_in_signed_material` is undefined (the signed material is body-only), while `shop_delivered_to_handler = request.shop`, an unauthenticated header value. Because the HMAC only proves "this body was produced by holder of `client_secret` for some shop," not "for shop X," an attacker who legitimately installs the app on their own store (an unprivileged action any internet user can perform) receives genuinely-signed webhook deliveries for their own shop. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the victim's shop domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it never inspected the header, and `WebhookMetadata.shop` is populated with the attacker-controlled victim domain.

### Impact Explanation
This allows cross-tenant confusion in the host application's webhook processing: business logic that is scoped/keyed by `WebhookMetadata#shop` (e.g., "look up merchant record for `shop`, then apply the webhook body to that merchant's data") can be tricked into acting on attacker-supplied data under a victim shop's identity, since the shop value delivered to `WebhookHandler#handle` carries no authenticity guarantee. This matches the Critical category of cross-tenant access, since the gem's own validation primitive (`HmacValidator`) is what falsely certifies the forged shop association as trustworthy.

### Likelihood Explanation
Requires only an unprivileged attacker with any Shopify development/test store (free) where the target app is installed, or the ability to trigger any webhook with attacker-controlled body content on that store, plus knowledge of the target app's webhook endpoint. No `client_secret`, access token, or privileged account for the victim shop is needed — replay of a legitimately-signed body against a different `shop-domain` header is sufficient. This is a real, currently reachable code path in `Registry.process`, not a theoretical one.

### Recommendation
Bind the shop identity to the signed material or otherwise authenticate `x-shopify-shop-domain` before trusting it: e.g., include the shop domain (and ideally webhook id / topic) in the HMAC-signed string in `to_signable_string`, or require the host application to independently verify that `request.shop` corresponds to a shop with an active, stored session/installation before processing, rather than treating the header as authenticated purely because `HmacValidator.validate` passed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and configures a webhook subscription (or otherwise triggers a webhook) whose body is fully attacker-controlled/attacker-known.
2. Shopify (or the attacker's own trigger) sends the app a webhook: body `B`, headers including `x-shopify-hmac-sha256: HMAC(B, client_secret)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`. The attacker captures `B` and the valid HMAC.
3. Attacker replays the same request to the app's webhook endpoint, keeping body `B` and the valid HMAC header unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) and matches, so validation succeeds: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled data is delivered to the host app under the victim's tenant identity, even though the victim never sent it and the signature never certified that association.

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
