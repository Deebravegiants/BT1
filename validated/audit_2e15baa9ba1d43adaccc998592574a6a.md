### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted from headers but excluded from the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verified by `Utils::HmacValidator.validate` binds solely to the JSON body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values—read straight from HTTP headers and handed to the app's `WebhookHandler`—are never part of the signed data, breaking the intended equality `HMAC-verified-shop == shop-acted-on`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC only over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` accepts the request once that body-only HMAC check passes, then dispatches the handler using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all of which are parsed straight from headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) with no cryptographic binding: [3](#0-2) [4](#0-3) 

The app-level `client_secret` used to compute the HMAC is shared across every shop that has the app installed (it is not per-tenant). Any user who installs the app on their own store is an "unprivileged internet user" relative to other tenants of the same app, yet Shopify will deliver them legitimate webhooks whose bodies are HMAC-signed with that shared secret. Because the signature covers only the raw body and not the headers, that user can capture a valid `(body, hmac)` pair from their own shop's webhook delivery and replay it to the app's webhook endpoint with a forged `shopify-shop-domain` header pointing at a different tenant (and/or a forged `shopify-topic`/`webhook-id`). The signature still validates because `to_signable_string` never included those fields, so `Registry.process` will pass a `WebhookMetadata` claiming a different `shop`/`topic` than the one that actually authored the payload: [5](#0-4) 

Any host application that uses `WebhookMetadata#shop` to key its per-tenant data store (the intended and documented usage pattern shown in the gem's docs) will write or act on the attacker-controlled body under a victim tenant's identity.

### Impact Explanation
This breaks the tenant-identity binding that the gem's own HMAC verification is supposed to provide (`shop-domain-header == shop-that-produced-the-hmac`). An attacker who legitimately installs the app on their own store can forge webhook deliveries that the receiving application will attribute to any other shop of their choosing, since `shop`/`topic`/`webhook_id` are not covered by the signature. This is cross-tenant data injection/corruption through the app's own webhook-processing primitive, not a defect of the host application ignoring documented behavior — the gem's own `process` method performs the dispatch using unauthenticated header values immediately after HMAC validation succeeds.

### Likelihood Explanation
Requires only that the attacker be able to install the target Shopify app on a shop they control (a normal onboarding action for any public app) and craft an HTTP request to the app's registered webhook endpoint with modified headers and the captured signed body — no access to the app's `client_secret`, an access token, or any other credential is needed.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in `Request#to_signable_string` (or otherwise cryptographically bind them, e.g. by validating them against server-side webhook-registration state) before they are trusted and passed to `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate Shopify webhook delivery with body `B` and header `x-shopify-hmac-sha256: H = HMAC(client_secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the same raw body `B` and signature `H` to the app's webhook endpoint but rewrites `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally `x-shopify-topic`).
3. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only [1](#0-0)  and it matches `H`, so `Registry.process` proceeds [3](#0-2) .
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` even though the body originated from the attacker's own shop, letting the attacker inject arbitrary attacker-controlled data under the victim tenant's identity.

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
