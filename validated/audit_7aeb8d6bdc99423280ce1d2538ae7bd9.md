### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then dispatches the *unauthenticated* `shop-domain` and `topic` HTTP headers straight to the host application's handler as the tenant identity and business-event type. Because the signature never covers these headers, any request carrying a genuine Shopify-issued `(body, hmac)` pair can be replayed with attacker-chosen `shop-domain`/`topic` headers and will still pass verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes and compares the HMAC exclusively against that signable string: [2](#0-1) 

`Registry.process` only checks this body-only HMAC before trusting the request's `shop` and `topic` accessors, which are read straight from headers with no additional check: [3](#0-2) [4](#0-3) 

This breaks the intended binding `authenticated(bytes) == acted_on(bytes)`: the bytes actually verified by HMAC are `raw_body` alone, while the bytes acted upon for tenant/topic dispatch are the `shopify-shop-domain` and `shopify-topic`/`x-shopify-topic` headers, which are never part of the signable string. Any party who can obtain one genuine `(raw_body, hmac)` pair signed by Shopify with the app's own `client_secret` (e.g., by installing the app on their own store and receiving a real webhook) can resend that exact body/hmac pair to the app's webhook endpoint while substituting a victim shop's domain in `shopify-shop-domain` and/or a different topic in `shopify-topic`. `HmacValidator.validate` will still return `true` because it only recomputes the signature over the body, and `Registry.process` will hand the forged `shop`/`topic` to the registered `WebhookHandler`, causing the host application to process attacker-supplied data as if it originated from a different, unrelated merchant.

### Impact Explanation
This allows cross-tenant data injection/confusion: an attacker-controlled webhook body can be attributed to any other shop domain the attacker chooses, and/or reinterpreted under an arbitrary topic (e.g. turning an `orders/create` payload into a `shop/redact` or `app/uninstalled` event for a victim shop). Depending on how the host app's `WebhookHandler` implementations use `shop`/`topic` (typically to look up the tenant's session/store and apply topic-specific business logic, including data-deletion compliance topics), this can lead to writing/deleting/mutating another merchant's records or triggering privileged compliance actions against the wrong tenant — a cross-tenant access impact.

### Likelihood Explanation
Requires the attacker to possess at least one valid `(body, hmac)` pair signed by the app's secret. This is trivially obtainable by any attacker who installs the target app on their own (or a free trial) Shopify store, since Shopify will deliver real, correctly-signed webhooks to that app for that store. The attacker then only needs to POST the same body/hmac to the app's public webhook endpoint with modified `shopify-shop-domain`/`shopify-topic` headers — no secrets, tokens, or privileged access are required beyond running an ordinary store.

### Recommendation
Include the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers in the signable content that `HmacValidator` verifies (e.g., have `Request#to_signable_string` incorporate these header values, or perform a secondary bound check), so the HMAC cryptographically binds the tenant/topic metadata to the payload rather than trusting them as unauthenticated headers.

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com` and configures a webhook (e.g. `orders/create`). Shopify delivers a POST with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker replays the exact same request to the app's public webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: shop/redact` (or any topic registered by the app)
   - keeps body `B` and `x-shopify-hmac-sha256: H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes HMAC over `B` only and matches `H` — validation succeeds.
4. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` and `topic: "shop/redact"`, causing the host application to execute victim-tenant business logic (e.g. data deletion, order creation, session lookups) using attacker-supplied content.

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
