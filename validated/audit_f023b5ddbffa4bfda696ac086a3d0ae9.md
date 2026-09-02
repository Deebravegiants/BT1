### Title
Webhook HMAC signs only the raw body, leaving `shop`, `topic`, and `webhook_id` unauthenticated — cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC that `Utils::HmacValidator.validate` checks in `ShopifyAPI::Webhooks::Registry.process` never covers the `shop`, `topic`, or `webhook_id` values that the host application actually acts on. Any party who can obtain one valid `(body, hmac)` pair signed with the app's shared secret can replay that body with forged `shopify-shop-domain` / `shopify-topic` headers, and the gem will report the request as authentic.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers without being part of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature only from `to_signable_string` (i.e. the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` trusts this validation result and then dispatches using the unauthenticated `request.topic` and `request.shop` fields: [4](#0-3) 

Because Shopify webhook HMACs are computed with the app's single shared `api_secret_key` (not a per-shop secret), any shop that has the app installed can legitimately receive webhooks with a valid `(body, hmac)` pair for that same secret. The binding the gem should enforce is:
`hmac == HMAC(secret, body || shop || topic || webhook_id)`
but what it actually enforces is:
`hmac == HMAC(secret, body)`
This equality gap is exactly the "field acted on but not covered by the HMAC" class: `shop` and `topic` are consumed by `WebhookMetadata`/handler dispatch but are excluded from the signed bytes.

### Impact Explanation
An attacker who operates any shop with the app installed (an ordinary unprivileged merchant of the app, not a privileged party) can capture a validly-signed webhook body/HMAC pair for events they control (e.g., by creating/updating a resource whose serialized JSON they can predict or influence), then replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop and/or the `shopify-topic` header for a different topic. `Utils::HmacValidator.validate` still returns `true` because it only checks the body bytes, so `Registry.process` will invoke the topic handler attributing the (possibly attacker-crafted) payload to the victim shop. Depending on how the host app uses `WebhookMetadata#shop`/`#topic` (e.g., updating per-shop records, revoking access, provisioning data), this enables cross-tenant data injection/corruption — one merchant forging events "from" another merchant's shop.

### Likelihood Explanation
Any merchant who installs the app (an unprivileged, unauthenticated-to-other-tenants actor from the app's perspective) can generate arbitrarily many valid `(body, hmac)` pairs by taking actions in their own store, then freely modify the `shop`/`topic` headers on replay since those are never covered by the signature. No access to `api_secret_key`, access tokens, or victim credentials is required — only ordinary use of the app as a legitimate customer of it and control over HTTP headers on the (replayed) request to the app's own webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed string computed by `to_signable_string` (or otherwise bind them cryptographically, e.g. by having the host verify that the resolved shop/topic match values embedded in the signed body), so `HmacValidator.validate` fails whenever any of these identity-bearing fields are altered relative to what was originally signed.

### Proof of Concept
1. Shop A installs the app and shares the app's single `api_secret_key`.
2. Shop A triggers an event (e.g., updates a product) causing Shopify to POST a webhook to the app with body `B` and header `shopify-hmac-sha256: HMAC(secret, B)`, `shopify-shop-domain: shop-a.myshopify.com`, `shopify-topic: products/update`.
3. The attacker (Shop A's owner) captures this `(B, hmac)` pair.
4. The attacker replays a POST to the app's webhook endpoint with the same body `B` and same `hmac`, but headers changed to `shopify-shop-domain: shop-b.myshopify.com` (victim shop) and/or a different `shopify-topic`.
5. `ShopifyAPI::Webhooks::Request.new` parses these forged headers; `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) still returns `true`, because `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) never included `shop`/`topic` in the signed bytes.
6. The registered handler is invoked with `WebhookMetadata.new(topic: "products/update", shop: "shop-b.myshopify.com", body: parsed(B), ...)`, causing the host application to process attacker-controlled data as if it originated from Shop B.

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
