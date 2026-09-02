Confirmed: `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC computed by `HmacValidator.validate_signature` covers only the request body, never the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers [2](#0-1) . Yet `Registry.process` trusts `request.shop` (parsed straight from the unauthenticated header) to build the `WebhookMetadata` handed to the host application's handler [3](#0-2) [4](#0-3) .

### Title
Webhook tenant identity (`shop`) is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — all derived from unauthenticated HTTP headers — are trusted and forwarded to the host application's webhook handler as the tenant identity.

### Finding Description
`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the signed payload [5](#0-4) . After HMAC validation succeeds (which only proves the *body* bytes are authentic for *some* shop that produced that exact body with the app's secret), `process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` and passes it to the registered handler as the trusted tenant context [3](#0-2) .

This is the same identity-binding class as the reported EigenPod bug: a value that is *acted upon* (the `shop` field used for tenant-scoped processing) is not covered by the authenticity check (the HMAC), so the two can be desynchronized. Concretely, the equality that should hold is:
`shop_that_produced(raw_body, secret) == shop_reported_in_header`
but only `hmac == HMAC(secret, raw_body)` is checked; `shop` is unconstrained.

### Impact Explanation
Any party who can obtain one genuine webhook delivery for a body/HMAC pair signed with the app's `client_secret` (e.g., by triggering an event on their own, attacker-controlled shop that has the app installed) can replay that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting an arbitrary victim `shopify-shop-domain` header. Because the signature never covered the shop header, validation still passes, and the host application's handler receives `WebhookMetadata` claiming the event belongs to the victim shop. If the host application uses `data.shop` to look up sessions, write data, or trigger side effects scoped by shop (the documented, expected usage pattern of this struct), this results in cross-tenant data corruction/access — a Critical-impact class per the given criteria.

### Likelihood Explanation
Exploitation only requires the attacker to operate one legitimate shop with the app installed (to legitimately obtain a valid HMAC/body pair) and the ability to send an HTTP request to the app's public webhook endpoint with a forged `shop-domain` header — no access token, secret, or privileged account is required. This is within the "unprivileged internet user" threat model.

### Recommendation
Bind the shop identity into the signed material, or independently verify `request.shop` against a shop known to have registered for that specific webhook (e.g., cross-check against the topic/webhook subscription records or reject if the resolved shop's session/webhook registration doesn't match). At minimum, document that host applications must not trust `WebhookMetadata#shop` as authenticated without further verification, or extend `to_signable_string`/HMAC scope to include the shop domain header so `HmacValidator` binds it.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the exact `raw_body` and the resulting `x-shopify-hmac-sha256` value from the real Shopify delivery.
2. Attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(secret, raw_body)` — unaffected by the header change — and returns `true` [2](#0-1) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the host application processes the forged body as if it originated from the victim shop [3](#0-2) .

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
