## Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then unconditionally trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers to build the `WebhookMetadata` passed to the app's handler. None of these header fields are included in the HMAC-signed payload, so the identity binding "the shop the handler acts on == the shop that produced this authenticated payload" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read directly from headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it against the `hmac-sha256` header: [3](#0-2) 

`Registry.process` gates on this HMAC check and then immediately uses the unauthenticated `request.shop` to build the tenant-identifying metadata delivered to the app's handler: [4](#0-3) 

Because a single app's `api_secret_key` is shared across every shop that has installed the app, any merchant who legitimately installs the app receives real webhooks with a valid `(body, hmac)` pair signed under that same shared secret. That merchant can capture one of their own genuine webhook deliveries and resend it to the app's webhook endpoint after swapping only the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header value to any other shop's domain. `HmacValidator.validate` still passes because it never inspects those headers — it only recomputes an HMAC over the untouched body. `Registry.process` then invokes the app's handler with `WebhookMetadata#shop` set to the attacker-chosen (victim) shop, `WebhookMetadata#topic` set to the attacker-chosen topic, while `body` is unrelated attacker-controlled content.

The identity equality that should hold — `shop_used_by_handler == shop_that_HMAC_authenticates` — is broken here because the HMAC authenticates only bytes, not any shop/topic claim.

### Impact Explanation
Any app relying on `ShopifyAPI::Webhooks::Registry.process`/`Request` to authenticate the source and target tenant of a webhook (a documented, intended usage pattern per `docs/usage/webhooks.md`) can be tricked into processing attacker-forged webhook payloads attributed to a shop the attacker does not own. Depending on the handler's logic (e.g., updating orders/inventory/customers for the "sending" shop, or triggering shop-scoped side effects keyed off `data.shop`), this results in cross-tenant data injection/corruption — data belonging to or associated with Shop B can be manipulated by an attacker who only controls Shop A. This matches the required "cross-tenant access" impact category.

### Likelihood Explanation
The attack only requires an attacker to be an ordinary, unprivileged merchant who installs the target app on their own store (a normal onboarding action, not a privileged operation) and to be able to POST arbitrary headers/body to the app's public webhook endpoint — which they can do without any special access, since they know their own valid `(body, hmac)` pairs from webhooks Shopify already delivered to them.

### Recommendation
Include the tenant-identifying and routing fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable string, or otherwise cryptographically bind them to the verified payload, so that tampering with these headers invalidates the signature. At minimum, document and/or enforce that consuming applications must independently verify `request.shop` against an expected/known shop (e.g., cross-check against their session store) before trusting it, since header values are not currently covered by `to_signable_string`.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify delivers a real webhook: body `{"id":1}`, header `x-shopify-hmac-sha256: H` (valid HMAC of the body under the shared `api_secret_key`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same body and `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body as usual; `Utils::HmacValidator.validate` recomputes HMAC over the (unchanged) body and it matches `H`, so validation passes: [5](#0-4) 
4. `Registry.process` calls the app handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: {"id"=>1}, ...)`, causing the app to process attacker data as if it originated from `victim-shop`.

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
