### Title
Webhook shop-domain (and topic/webhook-id) header trusted for tenant identification without HMAC coverage - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable content solely from the raw request body [1](#0-0) , while the `shop`, `topic`, `api_version`, and `webhook_id` values used to route and attribute the webhook are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC against the body only, then immediately trusts `request.shop` and `request.topic` to identify the tenant and dispatch to the handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop header used for tenant attribution == shop covered by the verified HMAC`. In this gem it does not. `Request#to_signable_string` returns `@raw_body` only [1](#0-0) , and `Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string using `Context.api_secret_key` [4](#0-3) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` (and sibling) headers with no cryptographic binding to the signed body at all [5](#0-4) .

`Registry.process` performs the HMAC check and then constructs `WebhookMetadata` directly from these unauthenticated header values, handing them to the app's registered handler as the tenant/topic of record [3](#0-2) . Because only the body bytes are verified, any request that carries a body+HMAC pair that is valid for *some* shop can have its headers rewritten to claim a *different* shop, topic, or webhook id, and the check still passes — the bytes verified (body) are not the bytes parsed for tenant identity (headers).

Concretely, a merchant/attacker who operates their own store receives genuine webhook deliveries from Shopify for their own shop, each with a valid `shopify-hmac-sha256` computed over the body with the app's `api_secret_key`. That attacker can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop, or substituting `shopify-topic`/`shopify-webhook-id` for a different registered topic. `Registry.process` still finds `Utils::HmacValidator.validate(request)` true (body/HMAC pair is legitimate) and dispatches the handler believing the event belongs to the victim shop/topic.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to guarantee for webhook consumers: the `shop` value handed to the app-defined `WebhookHandler` is meant to unambiguously identify which merchant the event is for, so host applications key their per-tenant state, side effects, and mandatory-compliance actions (e.g. `shop/redact`, `customers/redact`, `customers/data_request`) off it [6](#0-5) . Forging the shop attribution of an otherwise-legitimate signed payload is a cross-tenant data-integrity issue: it lets one authenticated merchant inject events that the app will process as belonging to another merchant's shop, without needing that merchant's access token or `client_secret`. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Requires only that the attacker run/control one installed shop of the app (an unprivileged, low-cost precondition — any merchant can install a public app) and be able to send an arbitrary HTTP POST with custom headers to the app's public webhook callback URL, which is by design internet-reachable. No access token, `client_secret`, or `api_secret_key` is needed — only replay of headers that this gem never binds to the signed body.

### Recommendation
Include the routing-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them (e.g., verify `shop` against the specific webhook subscription/registration the payload's HMAC was issued for) rather than trusting header values that fall outside the signable string in `Request#to_signable_string`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery, e.g. for topic `orders/create`, with body `B` and header `shopify-hmac-sha256: H` (valid because Shopify computed `H = HMAC-SHA256(api_secret_key, B)`).
2. Attacker replays `POST <app>/webhooks` with the same body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` runs `Utils::HmacValidator.validate(request)` [7](#0-6) , which passes because it only checks `B` against `H`.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [8](#0-7) , causing the app to process attacker-controlled order/customer data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
