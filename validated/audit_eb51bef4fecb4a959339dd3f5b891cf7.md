## Title
Webhook HMAC only authenticates the request body, not the `shop`/`topic`/`webhook_id` headers, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop as soon as `Utils::HmacValidator.validate(request)` succeeds. However, the HMAC signature only covers the raw request body — the `shop-domain`, `topic`, `webhook-id` and `api-version` headers that identify *which tenant and which event* the webhook is for are never included in the signed material. Since a single app's `api_secret_key` is shared across every shop that installs the app, any merchant who has installed the app on their own store can capture a validly-signed `(body, hmac)` pair from a real webhook Shopify sends them, then replay that exact body/HMAC pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header to a victim shop. The app will accept it as authentic and process it under the victim's identity, breaking the intended binding `authenticated_signer == processed_tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the HMAC solely over `verifiable_query.to_signable_string` (the body) and compares it to the received `hmac` header: [2](#0-1) 

`Registry.process` then trusts `request.shop`, `request.topic`, and `request.webhook_id` — all plain, unauthenticated headers — to build the data handed to the app's webhook handler, immediately after the (body-only) HMAC check: [3](#0-2) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from HTTP headers with no cryptographic binding to the signed body: [4](#0-3) 

Because the same `Context.api_secret_key` is used to validate webhooks for *every* shop that has the app installed (it's the app's secret, not a per-shop secret), a valid `(body, hmac)` pair obtained from one shop's real webhook is also "valid" HMAC-wise for a request that claims to be from a different shop. The equality that should hold — `shop identified by the signed payload == shop the handler acts on` — does not hold, because the shop identity is carried in an unsigned header, not in the signed payload.

### Impact Explanation
This crosses a tenant boundary: a merchant who has legitimately installed the target app (an "unprivileged" party with respect to *other* merchants' data) can forge webhook events attributed to any other shop using the same app, by simply changing the `X-Shopify-Shop-Domain` header on a replayed, validly-HMAC'd body. Depending on the handlers registered by the host application, this can drive destructive or sensitive operations against the victim tenant — e.g., mandatory compliance topics such as `shop/redact`, `customers/redact`, `customers/data_request`, or `app/uninstalled` handlers that delete/export the victim shop's data or tear down its session — using only the attacker's own (legitimately obtained) webhook traffic as raw material. This is a cross-tenant access/action vulnerability.

### Likelihood Explanation
Any user can sign up as a legitimate merchant, install the target app, and immediately start receiving genuinely-signed webhook deliveries for topics they can trigger themselves (e.g. `orders/create`, or any mandatory GDPR topic sent to every installed shop). Capturing the raw POST body and its `X-Shopify-Hmac-Sha256` header requires nothing more than logging their own inbound webhook traffic, which is fully attacker-controlled infrastructure. Replaying it with a modified `shop-domain` header against the app's public webhook endpoint is trivial and requires no secrets, tokens, or privileged access to the victim shop.

### Recommendation
Bind the shop (and ideally the topic) into the authenticated material, or otherwise verify that the `shop-domain` header used to route/attribute the event actually corresponds to a shop with an existing, previously-established session/installation record before acting on it — do not treat the header as trusted merely because the body's HMAC matches the app secret. At minimum, cross-check `request.shop` against the target application's own session store before invoking handlers, and document that a body-only HMAC does not authenticate the shop/topic headers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers (or waits for) a webhook, e.g. `customers/redact`, and captures the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` that Shopify sent (this is validly HMAC'd with the app's `api_secret_key`).
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: shop/redact` (or any topic registered by the app)
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` using the shared app secret [5](#0-4) .
5. `Registry.process` looks up the handler for the spoofed topic and invokes it with `shop: "victim-shop.myshopify.com"`, causing the host application to perform the corresponding action against the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
