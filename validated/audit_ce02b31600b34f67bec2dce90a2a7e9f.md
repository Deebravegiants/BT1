### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then trusts the `x-shopify-shop-domain` (or `shopify-shop-domain`) header as the tenant identity passed to the app's handler — without that header ever being part of the signed material.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` header using a constant-time compare: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body: [2](#0-1) 

The `shop` accessor is read directly from the `shop-domain` header, which is not part of that signable string and therefore is never authenticated by the HMAC: [3](#0-2) 

`Registry.process` verifies only the HMAC over the body, then forwards `request.shop` unchanged into `WebhookMetadata`, which is what the host application's handler uses to determine which merchant/tenant the payload belongs to: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `hmac == HMAC(api_secret_key, body || shop)`, i.e., the shop the handler is told the data came from should be cryptographically bound to the same secret-keyed signature that authenticates the payload. Instead the equality that actually holds is `hmac == HMAC(api_secret_key, body)` only — `shop` is asserted, not verified.

Because `api_secret_key` is a single value shared by the app across all installations/shops (not shop-specific), any entity that can obtain one genuine, validly-signed webhook delivery for their own shop (which any merchant can do simply by installing the app on their own store and triggering an event) possesses a `(body, hmac)` pair that will pass `HmacValidator.validate` regardless of which `shop-domain` header accompanies it. The header can be freely rewritten to name a different, victim merchant's shop domain, and `Registry.process` will accept it and hand it to the handler as if it were authentic data for that victim shop.

### Impact Explanation
This breaks the tenant boundary that host applications rely on this gem to enforce: `Registry.process` is the app's authentication gate for inbound webhooks, and it hands the handler a `shop` value that has no cryptographic relationship to the signature that supposedly authenticated the request. An attacker who owns any single shop with the target app installed can forge webhook deliveries "from" any other shop that also uses the app, causing the host app to process attacker-controlled data (order data, GDPR/compliance topics, uninstall notifications, etc.) under a different tenant's identity — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Exploitation requires only an unprivileged attacker who can install the app on their own store (a normal, unprivileged action for any Shopify merchant) to obtain one legitimate `(body, hmac)` pair, and the ability to POST to the app's public webhook endpoint with an arbitrary `shop-domain` header — no access to `api_secret_key`, tokens, or other credentials is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered material, or independently verify that the `shop-domain` header corresponds to a shop the app has an active installation/session for before dispatching to the handler, rather than trusting an unauthenticated header value as the tenant identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw body `B` and the genuine `x-shopify-hmac-sha256` header `H` computed as `HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a POST to the app's webhook endpoint with:
   - `x-shopify-hmac-sha256: H`
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: orders/create`
   - body: `B`
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [6](#0-5) .
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-supplied `victim.myshopify.com` header value and invokes the app's handler with data now attributed to `victim.myshopify.com` [7](#0-6) .

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
