### Title
Webhook shop attribution not bound to HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely by HMAC-validating the raw request body, but the `shop` field that is passed downstream to the app's webhook handler (and used to attribute the event to a specific merchant/tenant) is never included in the signed content. This breaks the identity binding `shop_that_signed_the_payload == shop_attributed_to_the_handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` only checks this body HMAC, and then dispatches the handler using `request.shop`, which is read directly from the unsigned `shop-domain` header: [3](#0-2) [4](#0-3) 

Since only the body is signed, an attacker who has legitimately installed the target app on their own Shopify store will receive genuine, correctly-HMAC-signed webhook deliveries for their own store (Shopify computes this HMAC using the app's shared secret, so the attacker needs no knowledge of `api_secret_key` to obtain a valid signature — they simply have to install the app on their own shop and capture a real delivery). The attacker can then replay that exact body + HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(topic:, shop: request.shop, ...)` attributing the (attacker-controlled) body content to the victim shop.

This is a "field acted on but not covered by the HMAC" defect: the `shop` value is trusted and acted upon (used as the tenant key for whatever the app does with webhook data — e.g., updating per-shop state, triggering per-shop side effects, writing to per-shop records) without being part of what the signature actually proves.

### Impact Explanation
Any application built on this gem that trusts `WebhookMetadata#shop` as the tenant identifier for processing incoming webhook data is exposed to cross-tenant data injection: an attacker with a legitimate (even free/trial) installation of the app on their own store can forge webhook events that the host app will process as if they came from an arbitrary victim shop. Depending on what the handler does with the data (e.g. creating orders/customers/records, updating billing/subscription state, or driving business logic keyed by shop), this can result in cross-tenant data corruption or unauthorized actions taken against another merchant's account — matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any consumer of this gem that does not add its own independent shop-header validation, because:
1. The library's own documentation (`docs/usage/webhooks.md`) presents `Registry.process` as sufficient webhook verification ("This will verify the request did indeed come from Shopify and then call the specified handler"), giving no indication that the `shop` field requires separate validation.
2. Obtaining a valid, real HMAC for a chosen shop is trivial for any attacker — install the app on their own store (a fully unprivileged, self-service action) and observe a genuine webhook delivery.
3. No component of the gem cross-checks `request.shop` against a known/authorized/installed session before invoking the handler.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signed content, or otherwise cryptographically bind them (e.g., verify the header value against an actively installed session/shop list, or require the host app to fetch the shop by API version + registered webhook_id rather than trusting the header value at face value) before constructing `WebhookMetadata`. At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is not covered by the HMAC and must be independently validated against the app's known/installed shops before being trusted as a tenant identifier.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers/receives a webhook (e.g. `orders/create`).
2. Shopify sends a POST to the app's webhook endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's `api_secret_key`, and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures the raw body and the `Hmac-Sha256` header value from this legitimate delivery.
4. Attacker replays the identical body and `Hmac-Sha256` header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `Registry.process` succeeds (it only checks the body against the HMAC), and the app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, processing it as authentic data belonging to the victim shop. [3](#0-2)

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
