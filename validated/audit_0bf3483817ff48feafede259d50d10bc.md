Confirmed: `to_signable_string` for webhook `Request` returns only `@raw_body` — the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are entirely excluded from the HMAC signature computation.### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted for tenant/handler dispatch despite being excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verification performed by `Utils::HmacValidator.validate` in `Registry.process` covers exclusively the request body. The `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers are read straight from unauthenticated HTTP headers and passed on, unverified, as the tenant identity (`shop`) and dispatch key (`topic`) for webhook processing.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are the two methods required by the `Utils::VerifiableQuery` interface, and `Utils::HmacValidator.validate` computes the signature exclusively from `to_signable_string`: [1](#0-0) [2](#0-1) 

Meanwhile, `shop`, `topic`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signed payload: [3](#0-2) 

`Registry.process` validates only the body's HMAC, then uses the unauthenticated `request.topic` to select the handler and the unauthenticated `request.shop` as the tenant identifier passed into the handler's `WebhookMetadata`: [4](#0-3) [5](#0-4) 

The binding that is broken is an equality that should hold but does not:
`shop-domain header used for tenant dispatch` ≠ `shop covered by the HMAC signature`.

This is structurally the same class of bug as the reported issue: a value (`seizeTokens`/`shop-domain`) is reused/trusted for a purpose (`repayAmount`/tenant identity) it was never cryptographically bound to. Any unprivileged internet user who can obtain one genuine, HMAC-valid webhook body (e.g., by triggering a webhook for their own store, which any merchant/dev account can do) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header. `HmacValidator.validate` will still succeed because it only ever hashes `@raw_body`, and `Registry.process` will hand the host application a `WebhookMetadata` claiming to originate from a different shop than the one that actually produced the signed body.

### Impact Explanation
This crosses a tenant boundary: a webhook payload legitimately generated for Shop A can be replayed and attributed by this gem to Shop B (or vice versa), because the gem does not authenticate which shop the signed bytes belong to — it only authenticates that the bytes were signed by *some* valid webhook with the app's shared secret. Any host application that uses `WebhookMetadata#shop` from this gem to look up state, session, or scoped resources for the shop (a common and encouraged pattern per `docs/usage/webhooks.md`) is exposed to cross-tenant data mixing driven entirely by this gem's failure to bind the identity field to the signature. This matches the "cross-tenant access" Critical impact category, since the merchant identity used for authorization/data-scoping downstream can be forged by anyone who can produce (or otherwise capture) one signed webhook body from any shop.

### Likelihood Explanation
Likelihood is constrained by the need to actually obtain a genuine, previously-signed body (webhooks are pushed, not pollable, and the HMAC secret is never exposed to the attacker). However, an unprivileged user who installs (or has access to) an app on their own store can trivially trigger and capture their own legitimate webhook deliveries (body + valid HMAC), then replay that exact body against the app's public webhook endpoint with a forged `shopify-shop-domain` header claiming a different shop. No secret material, TLS interception, or privileged account is required — only observation of one's own legitimately-received webhook traffic, which is available to any merchant.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material used for HMAC verification, or otherwise cryptographically bind `request.shop`/`request.topic` to the verified payload before they are trusted for dispatch or tenant scoping. Concretely, change `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` to incorporate the shop-domain header (matching Shopify's actual verification contract) rather than relying on `@raw_body` alone, so that a replayed body with a substituted `shop-domain` header fails HMAC validation.

### Proof of Concept
1. Attacker owns/operates Shop A with the target app installed, and legitimately receives (or otherwise captures) a real webhook delivery: body `B`, headers including `shopify-hmac-sha256: H(secret, B)` and `shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker resends this exact HTTP request to the app's webhook endpoint, changing only `shopify-shop-domain` to `shop-b.myshopify.com` (a different, unrelated merchant).
3. The host app calls `ShopifyAPI::Webhooks::Registry.process(request)`; `Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` only (unchanged) and returns `true`.
4. `Registry.process` looks up the handler for `request.topic` and invokes it with `WebhookMetadata.new(... shop: "shop-b.myshopify.com" ...)`, even though the payload `B` was never generated for, nor signed in relation to, Shop B — successfully attributing Shop A's webhook content to Shop B's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
