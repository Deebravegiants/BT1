## Title
Webhook HMAC only covers the raw request body, not the `shop-domain` header — attacker-controlled shop identity is trusted unauthenticated ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the `shop` value it exposes to the application comes from an HTTP header that is never included in the signed bytes. `Registry.process` validates the HMAC and then hands the *unauthenticated* `shop` value straight to the app's webhook handler, so a replayed, still-validly-signed body can be paired with an arbitrary victim shop domain.

### Finding Description
`Utils::HmacValidator.validate` verifies a signature over whatever `to_signable_string` returns for the `VerifiableQuery`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body — no headers are included: [2](#0-1) 

But `shop` is read from an HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`), which is not part of the signed content at all: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then unconditionally trusts `request.shop`, passing it into the handler's `WebhookMetadata`: [4](#0-3) 

The equality the gem implicitly assumes but never enforces is:

```
shop_bound_by_hmac == shop_used_by_handler
```

In reality, `shop_bound_by_hmac` is not defined at all — the HMAC only binds the body. `shop_used_by_handler` is taken verbatim from an attacker-reachable header. Any unprivileged user who can install the app on their own store (a normal, public flow) receives real webhook deliveries for that store, each with a valid `(body, hmac)` pair signed with the app's shared secret. That user can capture one such delivery and replay the identical `body`/`hmac` to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` dispatches the handler with `shop: <victim's domain>`.

### Impact Explanation
This is a cross-tenant identity confusion: data/action attribution in the webhook handler (which merchant a webhook event is "for") is fully attacker-controlled despite HMAC verification succeeding. Any host application that uses `request.shop` from a processed webhook to select which tenant's record to update, cache, or notify (the documented and expected usage pattern of `WebhookMetadata.shop`) can be made to apply an attacker's own webhook content under a victim shop's identity, or vice versa — a cross-tenant access primitive, which is explicitly a Critical-severity outcome per the classification used for this analysis.

### Likelihood Explanation
Likelihood is realistic: obtaining a valid `(body, hmac)` pair requires only that the attacker's own store install the app (ordinary, unprivileged action for any public Shopify app) and receive one real webhook delivery — no access to `api_secret_key` or any merchant's access token is needed. The header can be freely set by anyone submitting an HTTP request directly to the app's webhook endpoint, since this gem performs no binding between the header and the signed bytes.

### Recommendation
Include the shop-identifying header (and/or topic, webhook-id) in the signable string used for verification, or otherwise cryptographically bind `shop` to the signed payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document to consuming apps that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be relied upon for tenant selection without additional verification (e.g., cross-checking against a shop the app has an active installation/session for).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal public install flow) and configures a webhook subscription.
2. Shopify delivers a real webhook to the app: body `B`, header `shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), header `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends an HTTP POST to the app's webhook endpoint with the exact same body `B` and `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate(request)` calls `to_signable_string`, which returns only `B`, so the HMAC check passes.
5. `Registry.process` dispatches the registered handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` — the handler now processes attacker-supplied content as if it were `victim-shop`'s legitimate webhook, confirmed by [4](#0-3)  and [2](#0-1) .

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
