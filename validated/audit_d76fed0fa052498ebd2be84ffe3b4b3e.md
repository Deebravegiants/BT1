### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are trusted for tenant attribution while the HMAC only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body, then hands the un-authenticated `shop-domain` HTTP header straight to the app's handler as the tenant identifier. Because Shopify computes webhook HMACs with the app's single shared `client_secret` (not a per-shop secret), any merchant who has installed the app on their own store can capture a genuine `(raw_body, hmac)` pair from their own webhook deliveries and replay those exact bytes to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header. The HMAC check still passes (it never touches the header), and the gem reports the forged shop to the app as if it were authentic.

### Finding Description
`Utils::HmacValidator.validate` computes/compares the signature only over `to_signable_string`, which for webhooks is defined as the raw body: [1](#0-0) 
The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from HTTP headers and are never part of the signed material: [2](#0-1) 
`Registry.process` validates only the HMAC and then constructs `WebhookMetadata` using the unauthenticated `request.shop` value, passing it directly to the developer's handler: [3](#0-2) 
`Utils::HmacValidator.validate_signature` confirms the check is body-only: it signs `verifiable_query.to_signable_string` (the raw body for webhooks) with `Context.api_secret_key`, the single secret shared by the app across *all* installed shops: [4](#0-3) 

The equality that should hold is: **the shop identified by the authenticated bytes == the shop the handler is told the event came from**. Because the header is outside the HMAC, an attacker only needs a valid `(body, hmac)` pair produced by Shopify for *their own* shop (trivially obtainable by installing the app and receiving a real webhook) and can then freely rewrite the `shop-domain` header to point at any victim shop domain the attacker chooses. `Registry.process` cannot distinguish this from a genuine webhook for the victim shop, since the shared secret and lack of header binding make body-authenticity independent of shop-attribution.

### Impact Explanation
This breaks the shop-authentication boundary the gem's `Registry.process`/`WebhookHandler` API is meant to provide to app developers, who — per the gem's own documentation (`docs/usage/webhooks.md`) — are told that `process` "will verify the request did indeed come from Shopify" and are given `data.shop` as a trusted tenant identifier to key work off of (e.g., `perform_later(shop_domain: data.shop, ...)`). An attacker who is any legitimate (or trial) merchant on the platform can forge events attributed to an arbitrary victim shop, causing cross-tenant data confusion inside the host app (e.g., triggering the app to process/overwrite data, enqueue jobs, or update records keyed by `shop` for a shop the attacker does not control). This is a cross-tenant authentication/attribution bypass rooted entirely in this gem's `Webhooks::Request`/`Registry` implementation, not a misuse of a documented API by the host app.

### Likelihood Explanation
Likelihood is high for any developer following the gem's documented pattern exactly as shown (`data.shop` used as the tenant key with no additional verification), since the only prerequisite is the attacker having any Shopify store with the target app installed (no privileged credentials, no `client_secret`, no TLS interception needed) plus the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the verified payload before it is handed to `WebhookMetadata`/the handler. At minimum, the gem should document/enforce that `data.shop` from `Registry.process` must not be treated as authenticated on its own, and should provide (or require) a mechanism that ties the `shop-domain` header to a value derived from data that is actually covered by the signature (e.g., verifying the shop domain against the webhook subscription/ registration metadata associated with the specific webhook, if such data can be embedded and signed).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) to the app's registered endpoint, capturing the exact `raw_body` and `x-shopify-hmac-sha256` header value from that legitimate delivery.
2. Attacker crafts a new HTTP POST to the same app endpoint using the identical `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and any desired `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body against the shared `api_secret_key` — the check passes since the body+HMAC pair is genuinely valid. [3](#0-2) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, and the app performs whatever shop-scoped action it takes on webhook receipt (e.g., enqueue a job keyed by `shop_domain`) as if the victim shop had genuinely sent that event.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
