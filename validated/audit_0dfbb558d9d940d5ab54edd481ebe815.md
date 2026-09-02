### Title
Webhook `shop` identity is read from an unauthenticated header while the HMAC only signs the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's webhook handler from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but `Utils::HmacValidator` only verifies the raw request body against the HMAC signature. The header carrying the shop identity is never part of the signed material, so the binding `shop delivered to handler == shop that produced/signed the payload` is not enforced.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is read straight from an HTTP header with no cryptographic protection: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header value - it never incorporates the `shop` header into the signed data: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, with no additional check that the shop header matches the shop the payload was actually signed for: [4](#0-3) 

Because the HMAC is computed with the app's `client_secret` over the body bytes only, anyone who possesses one valid `(body, hmac)` pair — for example a merchant who has legitimately installed the app and receives their own signed webhooks — can replay that exact body+HMAC pair to the app's webhook endpoint while substituting an arbitrary value in the `shop-domain` header. `HmacValidator.validate` still returns `true` (it never looked at the header), and `Registry.process` forwards the attacker-chosen `shop` value to the handler as `WebhookMetadata#shop`, exactly as if Shopify itself had delivered that body for that shop.

### Impact Explanation
Apps built on this gem are expected to key their per-tenant data (sessions, orders, resource state, feature flags) off the `shop` value delivered via `WebhookMetadata#shop`/`Registration handler.handle`. Since that value is never bound to the signed payload, a merchant who controls one legitimate app installation (and thus one legitimate HMAC-signed webhook body) can forge webhook deliveries that are attributed to a different tenant's shop identity, letting them inject or corrupt data belonging to a shop they do not control. This is a cross-tenant boundary break stemming purely from a broken identity binding inside this gem's webhook verification path, matching the "field acted on but not covered by the HMAC" class described in the reference report.

### Likelihood Explanation
Exploitation only requires: (1) the attacker's own shop to have the target app installed (a normal, unprivileged merchant relationship — no leaked secrets, no privileged account, no TLS interception needed), and (2) intercepting/crafting an HTTP POST to the app's webhook endpoint with the legitimately-signed body/HMAC pair but an attacker-chosen `shop-domain` header. Both are within reach of an ordinary internet-facing merchant/attacker and require no access to `api_secret_key`.

### Recommendation
Bind the `shop` identity into the material that is cryptographically verified rather than trusting an unauthenticated header:
- Include the shop header value in the HMAC signable string (or otherwise cryptographically authenticate it), or
- Require host apps to cross-check `request.shop` against the sender-of-record for the OAuth session/access token that originally registered the webhook, and reject mismatches inside `Registry.process` before constructing `WebhookMetadata`.

### Proof of Concept
1. A merchant `attacker-shop.myshopify.com` installs the app and Shopify sends a legitimate webhook: body `{"id":123}"`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`, HMAC computed over the body with the app's `client_secret`.
2. Attacker intercepts this request before it reaches the app (e.g., via a local proxy under their control, since it is their own traffic) and rewrites only the header to `x-shopify-shop-domain: victim-shop.myshopify.com`, leaving body and HMAC untouched.
3. Forward the tampered request to the app's webhook endpoint. `Utils::HmacValidator.validate` succeeds because it only checks the untouched body against the HMAC. [4](#0-3) 
4. `Registry.process` calls `handler.handle` with `shop: "victim-shop.myshopify.com"` even though the payload was never produced for that shop, letting the attacker inject data attributed to the victim tenant.

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
