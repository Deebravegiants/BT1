## Title
Webhook shop-domain and topic headers are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` and `topic` values used by the library to route and label the webhook are read from unauthenticated HTTP headers that are never included in the signed payload. This breaks the intended binding `HMAC == f(shop, topic, body)` down to `HMAC == f(body)`, letting an attacker replay a genuine, HMAC-valid webhook body while forging the shop/topic headers to make the host application process it as an event from a different tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop` and `topic` — both used downstream to identify the tenant and dispatch the handler — are pulled straight from request headers, entirely outside the signed data: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` and `request.topic` to build the dispatched metadata: [3](#0-2) 

`HmacValidator.validate` confirms the signature against `verifiable_query.to_signable_string`, which for `Request` is just the body bytes — the identity fields (`shop`, `topic`) are never part of what's verified: [4](#0-3) 

This is exactly the identity-binding gap the report's bug class describes: a field acted upon (`shop`/`topic`, used to build `WebhookMetadata` and route to the app's handler) is not covered by the HMAC that's supposed to authenticate the whole message. Since Shopify signs webhooks with `HMAC(secret, body)` and does not include shop/topic in that computation itself, the gem's `Request#hmac`/`to_signable_string` faithfully mirrors that (this is consistent with Shopify's documented webhook verification scheme), but it means the gem provides *no* protection at all for header authenticity — any attacker who can capture one legitimate `(body, hmac)` pair (e.g., from webhooks delivered to their own installed instance of the app, which they legitimately receive) can replay that exact body+HMAC to the app's webhook endpoint with a forged `shopify-shop-domain` and/or `shopify-topic` header.

### Impact Explanation
An unprivileged user who has installed the app on their own shop (or otherwise observed one valid webhook delivery) can forge the `shop` attribution of a webhook payload, causing the host application (which relies on `ShopifyAPI::Webhooks::Registry.process` / `WebhookMetadata#shop`) to apply the replayed payload's data to a different, victim tenant's records. This is a cross-tenant boundary violation — data validated as authentic for shop A can be attributed to shop B purely by header manipulation, since the header is not bound to the signature.

### Likelihood Explanation
Moderate-to-high: any app developer/merchant with legitimate access to their own webhook deliveries (a completely unprivileged position relative to other tenants) has all they need — one real `(body, hmac)` pair for a topic they can trigger (e.g., `orders/create`) — to attempt replay against the same endpoint with a spoofed shop-domain header. No secret material, access token, or privileged account for the victim is required.

### Recommendation
Include `shop` and `topic` (and ideally `webhook_id`/`api_version`) in the value that is HMAC-verified, or independently bind the header-derived `shop`/`topic` to a value cryptographically tied to the request (not achievable by the gem alone since Shopify signs body-only) — at minimum, `ShopifyAPI::Webhooks::Registry.process` should not be treated by consuming apps as proof that the *shop* or *topic* claims are authentic; the library should document this gap explicitly, or offer a stricter validation path that rejects requests where the shop cannot be otherwise corroborated (e.g., against a known/expected shop for the endpoint) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with the exact same body `B` and header `H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H` [5](#0-4) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com` [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
