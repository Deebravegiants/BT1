### Title
Webhook `shop-domain` / `topic` headers are trusted for tenant routing but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its webhook signature over the raw HTTP body only, yet `ShopifyAPI::Webhooks::Registry.process` uses the unsigned `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers to route the request and to identify the tenant (`shop`) passed to the app's handler. Any bytes an attacker controls that aren't part of the signed payload can be substituted without invalidating the HMAC check, breaking the binding `shop authenticated == shop acted on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic linkage to the signed body: [2](#0-1) 

`HmacValidator.validate` only ever hashes `to_signable_string` (the body) with the shared secret: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authenticating the *whole request*, then forwards the unsigned `request.shop` and `request.topic` header values to the merchant-facing handler as if they were verified: [4](#0-3) 

The binding that should hold is:

`HMAC-authenticated bytes (raw_body) == bytes used to determine tenant identity (shop-domain header)`

but the shop-domain/topic/webhook-id/api-version headers are outside the HMAC-covered bytes, so this equality is never enforced. A party that can obtain even one genuine `(body, hmac)` pair for a given app (e.g., because they install the same app on their own store and thus legitimately receive real, correctly-signed webhooks from Shopify) can replay that exact `body`/`hmac` pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header for a victim shop's domain (and/or the topic header for a different topic that the handler treats specially). `Utils::HmacValidator.validate` still returns `true` because the signature only covers the body, and `Registry.process` will dispatch the handler with `WebhookMetadata` claiming the request came from the victim shop.

### Impact Explanation
This crosses the tenant boundary defined by "shop-domain" without possessing any secret material: the attacker only needs their own legitimately-signed webhook (or a captured/observed one) and never needs `api_secret_key`, an access token, or the victim's credentials. Any host application that relies on the `shop` (and/or `topic`) value inside `WebhookMetadata` to decide which merchant's record to update, delete, or resync (a documented and expected usage pattern of `ShopifyAPI::Webhooks::Registry.process`) can be tricked into acting on behalf of, or against, a different merchant than the one whose data actually produced the signed body — a cross-tenant confusion within the boundary this gem is meant to guarantee ("this webhook genuinely originates from shop X").

### Likelihood Explanation
Likelihood is high for any developer who installs their own instance of the target app (a completely unprivileged, ordinary Shopify merchant action) — this legitimately yields real `(body, hmac)` pairs signed with the app's shared secret for arbitrary topics they can trigger (e.g., `orders/create`), which can then be replayed against the app's public webhook endpoint with a forged `shop-domain` (and/or `topic`) header, since nothing in this gem binds those headers to the signature.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable content, or independently verify that the shop-domain header value is one the app has an active session/installation record for before trusting it. At minimum, `Request#to_signable_string` should incorporate the shop and topic headers so that `HmacValidator.validate` fails if they are altered post-signing, restoring the binding between the authenticated bytes and the bytes used for tenant/topic routing.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers `orders/create`, capturing the resulting legitimate webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(secret, B)`).
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `B`, matching `H` (see `lib/shopify_api/utils/hmac_validator.rb` lines 26-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38).
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-200), where `shop` is `"victim-shop.myshopify.com"` even though the payload actually came from the attacker's own store — demonstrating the identity-binding break.

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
