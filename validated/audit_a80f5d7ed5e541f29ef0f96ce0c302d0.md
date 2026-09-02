### Title
Webhook `shop` field used by handlers is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` value dispatched to the app's webhook handler is taken from an unauthenticated HTTP header. Any party able to obtain one genuine, validly-signed webhook body/HMAC pair for their own shop (e.g. a merchant who has installed the app — an "unprivileged" actor relative to other tenants) can replay that exact body/HMAC with a different `shopify-shop-domain` header, and `Webhooks::Registry.process` will accept it as valid and hand the attacker-chosen `shop` to the handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` verifies the HMAC strictly against `to_signable_string`: [2](#0-1) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signable string at all: [3](#0-2) 

`Registry.process` validates the HMAC (which covers body only) and then dispatches to the handler using this unauthenticated `shop` value, with no cross-check that the `shop` in the header actually corresponds to any session/tenant the app expects for that payload: [4](#0-3) 

The binding the gem should be enforcing is:
`hmac_valid(raw_body) == true` ⇒ `shop header value == the tenant that produced/owns raw_body`

But because `shop` is excluded from the signed content, the equality that actually holds is only `hmac_valid(raw_body)`, decoupled from `shop`. A legitimate, low-privilege party who has the app installed on their own store receives real webhooks for their own store — each with a body and a *correctly computed* HMAC for that body. Since the header carrying `shop` is not signed, that same (body, hmac) pair remains valid for the library's verification step even after being resent with a different `shopify-shop-domain` header value naming a victim shop. `Registry.process` will still call the handler, passing through the attacker's chosen `shop` as `WebhookMetadata#shop`, giving the attacker the ability to make the app believe the payload originated from a different tenant.

### Impact Explanation
This is a cross-tenant identity-binding failure: the library allows a webhook payload (body content) to be dissociated from the shop it is attributed to for handler logic. Any app that keys tenant-scoped side effects (order/inventory updates, uninstall processing, subscription/billing state, cache invalidation, per-shop data writes) off `WebhookMetadata#shop` without separately re-validating that shop against its own list of known/installed shops can be made to apply another merchant's webhook to the attacker's chosen shop, or vice versa — a cross-tenant access/integrity issue.

### Likelihood Explanation
Exploitation requires only that the attacker operates their own shop with the app installed (no privileged credentials, no access token, no `client_secret`, and no interception of anyone else's traffic) — squarely an "unprivileged internet user" position. They can capture their own genuine webhook deliveries (valid body+HMAC), then re-POST that exact request to the app's webhook endpoint with a forged `shopify-shop-domain` header. The library performs no additional binding between the signed bytes and the shop header, so likelihood of success is high wherever the host app trusts `WebhookMetadata#shop` for tenant scoping without independent verification.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable string used for HMAC verification, or require callers to independently validate `request.shop` against a shop known to have generated a session/installation before trusting it in the handler, and document this requirement prominently for consumers of `Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets it receive a legitimate webhook, capturing the raw body `B` and header `shopify-hmac-sha256: H` (computed as `HMAC-SHA256(secret, B)`).
2. Attacker resends an HTTP request to the app's webhook endpoint with:
   - body: `B` (unchanged)
   - header `shopify-hmac-sha256: H` (unchanged, still valid since HMAC only signs body)
   - header `shopify-shop-domain: victim-shop.myshopify.com` (forged)
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == H`: [5](#0-4) 
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed_body, ...))`, and any app logic that trusts `shop` for tenant scoping now acts on the victim shop using attacker-controlled body content.

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
