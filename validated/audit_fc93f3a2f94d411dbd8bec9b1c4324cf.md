Confirmed: `VerifiableQuery` requires only `hmac` and `to_signable_string`, and for webhooks, `to_signable_string` returns only `@raw_body`, so the HMAC never binds `shop`, `topic`, or `webhook_id`.### Title
Webhook shop/topic identity not bound by HMAC allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then trusts the `shop-domain` and `topic` HTTP headers — which are never covered by that signature — to decide which tenant/handler the payload belongs to. This mirrors the report's bug class: a value used for a downstream decision (`shop`) is not the value actually bound by the cryptographic check (`raw_body`), breaking the equality `HMAC-verified bytes == identity used for dispatch`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose `to_signable_string` for webhooks returns only the raw body: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors read directly from HTTP headers that are not part of the signed content at all: [2](#0-1) 

`Utils::HmacValidator.validate` computes/verifies the HMAC purely against `to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` performs exactly one authenticity check — the body HMAC — and then immediately trusts the unauthenticated `request.shop` and `request.topic` header values to route the payload to the tenant-specific handler: [4](#0-3) 

Because the app's `api_secret_key` is a single value shared across every shop that has installed the app, any two webhooks signed with that same secret produce HMACs that are valid regardless of which shop or topic header accompanies them. The signature therefore proves only "this body+secret pair is authentic," never "this body belongs to this shop" or "this body is for this topic."

### Impact Explanation
An unprivileged user who installs the app on their own (attacker-controlled) shop receives genuine webhooks with valid `(raw_body, hmac)` pairs signed by the shared `api_secret_key`. That user can capture one such pair and replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a *different*, victim merchant's shop. `HmacValidator.validate` still passes because it only checks the body against the secret, and `Registry.process` dispatches the (attacker-supplied) payload to the handler tagged with the victim's shop identity. Depending on the host application's handler logic (e.g., updating orders/inventory/customer records keyed by `shop`), this enables cross-tenant data injection or state corruction — the merchant boundary the gem is expected to enforce is not actually enforced by the signature it verifies.

### Likelihood Explanation
Reachable by any actor who can install the app on a shop they control (a normal, unprivileged flow for any public/embedded Shopify app) and who can reach the app's public webhook HTTP endpoint — no leaked credentials, TLS interception, or privileged account required. The only skill required is capturing one legitimate webhook body/HMAC pair from their own shop and replaying it with modified headers.

### Recommendation
Include the identity fields that downstream code relies on (at minimum `shop-domain`, and ideally `topic`) in the signed material that `to_signable_string` returns for webhook requests, or otherwise cryptographically bind them (e.g., verify HMAC over `shop + topic + body`, or require the caller to independently confirm the `shop` header value matches a shop the app has an active session/webhook registration for) before dispatching to a handler.

### Proof of Concept
1. Install/authorize the target app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a request with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's shared `api_secret_key`.
2. Capture the raw body and the `x-shopify-hmac-sha256` value from that request.
3. Replay an HTTP POST to the app's webhook endpoint with the identical raw body and HMAC header, but set `x-shopify-shop-domain: victim.myshopify.com` (and, if desired, a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the shared secret.
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"`, causing the app to process attacker-controlled data under the victim tenant's identity.

### Citations

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
