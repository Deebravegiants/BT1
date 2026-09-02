### Title
Webhook shop-domain and topic are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop` and `topic` are read directly from HTTP headers that are never included in the HMAC-signed payload. Any party that can obtain one genuine, validly-signed webhook body/HMAC pair (trivially available to any merchant who installs the app, since the app's webhook endpoint receives real Shopify webhooks for that merchant's own shop) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` and `x-shopify-topic` headers to impersonate a different tenant or a different event type.

### Finding Description
`Utils::HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string`: [1](#0-0) 
For webhooks, `to_signable_string` is defined as only the raw body: [2](#0-1) 
But `shop` and `topic` — the values that determine *which tenant* and *which handler* the payload is routed to — come straight from attacker-controllable headers, unauthenticated by the HMAC: [3](#0-2) 
`Registry.process` trusts these unauthenticated fields directly after only checking that the *body* HMAC is valid: [4](#0-3) 

The broken identity binding, as an equality: the gem verifies `HMAC(raw_body) == received_hmac`, but the application then acts on `(shop_header, topic_header, raw_body)` as an atomic authenticated unit — `shop_header` and `topic_header` were never part of what was verified. `verified_bytes != acted_on_bytes`.

### Impact Explanation
An unprivileged actor who has installed (or has access to) the target app on their own Shopify store receives genuine, correctly-HMAC-signed webhooks from Shopify for that store. Because `shop` and `topic` sit outside the signed payload, that actor can replay the exact same `raw_body`/`hmac-sha256` pair to the app's public webhook endpoint while forging `x-shopify-shop-domain` to name a victim shop (and/or `x-shopify-topic` to change the routed handler). `HmacValidator.validate` still returns `true` because only the body is checked, and `Registry.process` dispatches the forged data to the handler tagged with the victim's shop id via `WebhookMetadata` built from `request.shop`. This is a cross-tenant data-integrity/authentication-boundary break: the host application's webhook handler cannot distinguish a validly-signed-but-wrong-tenant payload from a genuine one, which can corrupt per-shop state, trigger cross-tenant side effects (e.g. GDPR/redact flows, order/inventory updates) for a shop the attacker does not control.

### Likelihood Explanation
Requires only: (1) installing the target app on an attacker-owned/controlled shop (a normal, low-privilege action for any Shopify merchant if the app is public or the attacker can create a dev/trial store), and (2) capturing one legitimately delivered webhook to replay with modified headers against the app's public webhook endpoint. No access to `api_secret_key` or any merchant's access token is needed. This is a realistic, low-effort attack path for any external, unprivileged actor.

### Recommendation
Bind `shop` and `topic` (and any other header-derived fields the application relies on for routing/tenant identity) into the HMAC-signed payload, e.g., include them in the canonical string used for signature verification, or independently verify that the `shop` header matches an already-authenticated session/shop the app expects for that webhook subscription before dispatching to handlers. At minimum, document that `Registry.process` provides no authentication of the `shop`/`topic` headers, and require callers to cross-check `request.shop` against the shop associated with the webhook subscription record.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com`; app registers webhook for e.g. `orders/create`.
2. Shopify delivers a real webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>` and some `raw_body`.
3. Attacker captures this raw body and HMAC, then sends a new HTTP request to the same app endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates successfully because it only hashes `raw_body`: [2](#0-1) 
5. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though that shop never sent this webhook: [5](#0-4)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
