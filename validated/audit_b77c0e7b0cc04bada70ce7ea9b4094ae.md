### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook using `Utils::HmacValidator.validate(request)`, which validates the HMAC against `request.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw HTTP body — it never includes the `shopify-shop-domain` (or `x-shopify-shop-domain`) header. Despite this, `request.shop`, taken directly from that unauthenticated header, is passed straight into the webhook handler as the tenant identifier. This breaks the identity binding `shop_verified_by_hmac == shop_used_by_handler`: the HMAC proves the *body* is authentic, but proves nothing about which shop it belongs to.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

Meanwhile `shop` is parsed straight from an attacker-controllable header with no cryptographic tie to the HMAC: [3](#0-2) 

`Registry.process` verifies only the HMAC of the body, then forwards `request.shop` — the unauthenticated header value — directly into the handler as the tenant-identifying field, with no independent check that the shop matches the body's origin: [4](#0-3) 

Because the shop header is excluded from the signed content, a body/HMAC pair that is genuinely valid for one shop remains valid (HMAC still matches) when replayed with a different `shopify-shop-domain` header value. Any user who legitimately receives real webhooks for their own shop (i.e., any merchant who installs the app) can capture a valid `(raw_body, hmac)` pair and re-send it to the app's public webhook endpoint while substituting a different shop's domain in the header. `Registry.process` will treat it as a passing signature and dispatch `WebhookMetadata.new(topic:, shop: <attacker-chosen shop>, body:, ...)` to the app's handler, since: [5](#0-4) 

An unprivileged internet user only needs their own legitimate shop installation of the app (no `api_secret_key`, no access token, no privileged account) to forge cross-tenant-attributed webhook events.

### Impact Explanation
This crosses a tenant boundary: data legitimately generated for shop A (whose merchant is an ordinary, unprivileged app user) can be replayed and re-attributed to shop B purely by rewriting a header the gem never authenticates. Any host app that uses the `shop` field from `WebhookMetadata` to select which tenant's records to update (the documented and expected usage pattern shown in `docs/usage/webhooks.md`) can be made to apply attacker-supplied data to another merchant's account — a cross-tenant access/data-integrity violation, meeting the Critical bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Any merchant who installs the app can receive genuine webhooks for their own store and thus obtain a valid `(body, hmac)` pair at will (e.g., by placing an order to trigger `orders/create`). Forging the `shopify-shop-domain`/`x-shopify-shop-domain` header on the replayed request requires no secret knowledge — only the ability to POST to the app's public webhook endpoint. No credentials, tokens, or elevated access are needed.

### Recommendation
Include the shop-identifying header (and ideally topic/webhook-id) in the signed content verified against the HMAC, or independently authenticate/authorize the `shop` value (e.g., cross-check it against a shop that the app has an active installation/session for) before dispatching to handlers, rather than trusting the unauthenticated `shopify-shop-domain` header as-is.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`), capturing the raw body and the valid `X-Shopify-Hmac-Sha256` value Shopify sent.
2. Attacker POSTs to the app's webhook route with the exact same raw body and HMAC header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the headers; `Utils::HmacValidator.validate` succeeds because `to_signable_string` only checks the (unmodified) raw body.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker's own order data>, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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
