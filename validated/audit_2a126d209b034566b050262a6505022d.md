### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) fields are not covered by the HMAC signature, allowing cross-tenant webhook forgery via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates its HMAC only over the raw HTTP body, while the `shop` (tenant) attribution, `topic`, `api_version`, and `webhook_id` are all read from unauthenticated HTTP headers that are never part of the signed payload. Any party in possession of one genuine, HMAC-signed webhook delivery (e.g., a malicious merchant who installed the app and receives real webhooks for their own store) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop. The HMAC check passes because it never covered the shop header, and the handler is invoked believing the event belongs to the victim tenant.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all sourced purely from request headers, with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string` (i.e., the body), never incorporating the shop/topic headers into the signed message: [3](#0-2) 

`Registry.process` trusts `request.shop` (and `request.topic`) after only that body-only HMAC check succeeds, then forwards them unchanged to the app's handler as the tenant identity for the event: [4](#0-3) 

This breaks the identity binding: `HMAC-verified(shop header) == shop used to attribute/act on the event` is false — the equality actually enforced is only `HMAC-verified(body) == body`, while `shop` (and `topic`) ride along unauthenticated in headers that the gem's own `Request` class exposes as authoritative (`request.shop`) to the rest of the library and to consuming applications.

### Impact Explanation
A merchant who has legitimately installed the app on their own shop receives real, validly-signed webhook deliveries. Since the signature covers only the body, that merchant can capture one such delivery and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to an arbitrary victim shop domain (and the `webhook-id`/`api-version` headers altered as desired). `ShopifyAPI::Webhooks::Registry.process` will still consider the HMAC valid (body unchanged) and will hand the app's registered handler a `WebhookMetadata` claiming to originate from the victim shop. Any app logic that trusts `data.shop` to select a session, write per-tenant state, or take shop-scoped actions is thereby driven by attacker-controlled tenant attribution — a cross-tenant data confusion/access issue.

### Likelihood Explanation
Exploitation requires only that the attacker be a valid, unprivileged installer of the app on any shop (no elevated privileges, no access token theft, no TLS interception) — a bar met by any internet user who can install a public app. Capturing one webhook delivery to their own endpoint and replaying it with a modified header is trivial and requires no cryptographic material beyond what Shopify already legitimately sent them.

### Recommendation
Include the tenant-identifying and event-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed/verified material, or otherwise cryptographically bind them to the body before trusting `request.shop`/`request.topic` downstream — e.g., by requiring the consuming application to independently confirm the header-derived shop against a shop it already has an established, authenticated session/relationship with, rather than treating the header as ground truth solely because the body-only HMAC passed.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify sends a real webhook, e.g. `orders/create`, with body `B`, and headers including `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures this request (they control the endpoint receiving it, or a proxy in front of it).
3. Attacker resends the same body `B` and the same `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers/body; `Utils::HmacValidator.validate` succeeds because `to_signable_string` is `B` and the HMAC over `B` still matches. [5](#0-4) 
5. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"`, even though the event was never generated for that shop, allowing cross-tenant data/action confusion in any app that trusts this field.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
