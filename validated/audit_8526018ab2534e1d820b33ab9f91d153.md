This confirms the vulnerability. The `Registry.process` method verifies HMAC only over the raw body, then trusts the `shop-domain` header without any cryptographic binding.### Title
Webhook shop-domain identity spoofing via HMAC coverage gap — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` verifies is computed only over the raw request body. The `shop` field is never part of the signed bytes, so the binding "HMAC-verified bytes == bytes the app uses to attribute the event to a tenant" is broken.

### Finding Description
`Registry.process` validates a webhook solely via: [1](#0-0) [1](#0-0) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

The HMAC validity check calls `Utils::HmacValidator.validate`, which computes the signature over `request.to_signable_string`: [2](#0-1) 

```ruby
def to_signable_string
  @raw_body
end
```

Only `@raw_body` is signed. Meanwhile `shop` — the value the host application uses to decide *which tenant's data/session* the webhook event pertains to — is read straight from an unauthenticated header: [3](#0-2) 

```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

This is precisely the "field acted on but not covered by the HMAC" bug class: `bytes_verified(raw_body) != bytes_used_for_identity(shop_header)`.

Concretely, any merchant that installs the app (an "unprivileged internet user" from the perspective of *other* tenants) legitimately receives real, correctly-HMAC-signed webhooks from Shopify for their own shop and topics they control (e.g. by triggering an event on their own store, such as `orders/create` or `app/uninstalled`, or reusing a stored HMAC-signed payload). Because `shop-domain` is not included in the signable string, that attacker can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (or `shopify-shop-domain` in the new format) with a victim shop's domain. The signature still validates (`OpenSSL.secure_compare` only checks body-derived bytes), and `WebhookMetadata` is constructed with `shop: request.shop` pointing at the victim, while `body`/`topic` are attacker-controlled/attacker-signed content originally meant for the attacker's own shop.

### Impact Explanation
Downstream, host applications (e.g. built on top of `ShopifyApp`/`shopify_api`) look up a merchant's session/state keyed by `WebhookMetadata#shop` to decide what data to modify, delete, or resync (this is the documented purpose of the `shop` field passed to `WebhookHandler#handle`). By spoofing `shop`, an attacker who is a legitimate merchant for their own store can trigger the app to act on a **different tenant's** stored session/data using a payload the attacker fully controls the shape of (as long as it parses under the target topic), because the shop attribution is not cryptographically bound to the signed payload. This directly matches the Critical-severity category "cross-tenant access," since no data belonging to the victim's tenant is required to construct the forged request — only the attacker's own legitimately-signed webhook.

### Likelihood Explanation
High reachability: any actor who can install the app on their own store (a normal, low-privilege pathway) can obtain a validly HMAC-signed body/topic pair, and only needs to change one HTTP header before delivering it to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or the victim's environment is required. The only constraint is that the forged event must be processed identically regardless of the true originating shop, which is true by construction since the library performs no additional binding.

### Recommendation
Include `shop` (and ideally `topic`/`webhook-id`) as part of the signed/verifiable material, or otherwise cryptographically bind the shop-domain header to the signature before trusting it for tenant attribution — e.g., have `VerifiableQuery`/`to_signable_string` incorporate the relevant Shopify headers, or independently verify that the `shop-domain` header corresponds to a shop that is actually authorized/subscribed for that specific webhook subscription, rather than trusting the header verbatim once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and, through normal merchant actions, causes Shopify to send a legitimately signed webhook (raw body `B`, HMAC `H = HMAC_SHA256(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`).
2. Attacker replays the exact same body `B` and HMAC header `H` to the app's public webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body`, i.e. `B`) — this still matches `H`, so validation succeeds.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"`, and the host application's handler acts on the victim tenant using attacker-controlled body content, achieving cross-tenant impact without ever possessing the victim's credentials.

### Citations

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
