## Title
Webhook shop attribution can be forged because `shop-domain` is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the webhook's `shop` from an HTTP header, but the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies only covers the raw request body. An attacker who can obtain a validly-signed webhook body (e.g., by installing the app on their own store, which shares the same app-level `client_secret`) can replay that body with a forged `x-shopify-shop-domain`/`shopify-shop-domain` header pointing at a victim shop. The HMAC check still passes because it never binds the `shop` value, letting the attacker's webhook be attributed to another tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop` is read straight from an HTTP header, entirely outside of the signed material: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, raw_body)` and compares it to the `hmac-sha256` header — it never touches `shop`: [3](#0-2) 

After that check passes, the (attacker-controlled) `shop` header is forwarded verbatim to the app's handler as the tenant identifier: [4](#0-3) 

Because a single `client_secret` is shared by the app across **every** shop that installs it, and only the request body — not the shop — is bound by the HMAC, any party who can install the app on their own store (or otherwise obtain one validly-signed webhook payload) can capture a `(body, hmac)` pair and replay it against the app's public webhook endpoint with the `shop-domain` header rewritten to a different, victim shop domain. The signature check in `Utils::HmacValidator.validate` succeeds because the equality it actually enforces is `HMAC(secret, body) == received_hmac`, not `HMAC(secret, body ‖ shop) == received_hmac`. This breaks the intended binding "the shop asserted in the request equals the shop that produced the signed payload."

### Impact Explanation
This crosses a tenant boundary: the app's webhook handler will process attacker-supplied data (order/product/customer payloads the attacker fully controls, since it's their own store's webhook body) while believing it originates from a different, victim merchant. Depending on how the host app keys writes/side effects off `WebhookMetadata#shop`, this can lead to cross-tenant data corruption, incorrect authorization decisions, or injection of attacker-controlled data into another tenant's records — matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP request to the app's public webhook endpoint (unprivileged internet capability, no access token or `client_secret` needed) and knowledge of one legitimately-signed webhook body/HMAC pair, obtainable trivially by installing the app on any store (including a free/dev store) and capturing one of its own outgoing webhooks. This is an unauthenticated-attacker-reachable manipulation of an identity-binding field, fitting the "field acted on but not covered by the HMAC" analog class.

### Recommendation
Include the shop domain (and ideally the webhook topic/id) inside the signed material checked in `to_signable_string`, or otherwise cryptographically bind the `shop-domain` header value to the HMAC computation rather than trusting it as an independent, unauthenticated header. At minimum, document/enforce that consumers must cross-check the resolved shop against a known/installed-shop allowlist before acting on webhook data.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`.
2. Trigger any webhook topic the app subscribes to; capture the raw body `B` and its `x-shopify-hmac-sha256` header `H` (valid because `H = HMAC-SHA256(client_secret, B)`).
3. Replay a request to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds since it only checks `B` and `H`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `shop: "victim-shop.myshopify.com"` even though the payload actually came from the attacker's own store.

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
