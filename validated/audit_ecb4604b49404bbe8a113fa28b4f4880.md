### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC of the raw request body, but then trusts the `shopify-shop-domain` HTTP header — which is *not* part of the signed material — as the identity of the shop the webhook belongs to. This breaks the binding `shop authenticated == shop acted on`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor, however, is read straight from the unsigned `shopify-shop-domain` (or `x-shopify-shop-domain`) header: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only checks that `HMAC(secret, raw_body)` matches the `hmac` header — it never touches `shop`: [3](#0-2) [4](#0-3) 

Once validated, the unauthenticated `request.shop` value is forwarded directly to the app's handler as the trusted tenant identifier: [5](#0-4) 

Critically, the webhook HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across **every** shop that has installed the app — it is not a per-shop secret. This means any body+HMAC pair that is valid for one installed shop's webhook is equally "valid" (in the sense that the signature check passes) for a forged request bearing a different `shopify-shop-domain` header, because that header is outside the signed payload.

### Impact Explanation
An unprivileged party who merely installs the app on their own store (a normal, low-privilege action requiring no special credentials) can capture a body+HMAC pair from one of their own genuine webhook deliveries, then replay it with the `shopify-shop-domain` header changed to a victim shop's domain. `Registry.process` will accept the HMAC as valid and dispatch the handler with `shop: <victim-shop>`, causing the app to process attacker-chosen webhook content (e.g., `orders/create`, `app/uninstalled`, GDPR topics, etc.) as if it originated from the victim tenant. Any app logic keyed off `WebhookMetadata#shop` (data updates, uninstall/cleanup, entitlement changes) can be triggered against a shop the attacker does not control — a cross-tenant boundary violation.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (the normal SaaS case): the attacker only needs to install the app themselves (no elevated privileges, no access to the victim's tokens or the app's `client_secret`) and can freely choose/replay a body whose HMAC they can obtain from their own legitimate webhook traffic, then swap the header when re-delivering it to the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the signed material actually verified, or otherwise cryptographically tie the `shopify-shop-domain` header to the specific installation before trusting it — e.g., cross-check `request.shop` against a shop known to have that specific `webhook_id`/subscription registered (looked up from the app's own store), or require the caller to additionally validate the shop against a per-shop secret/session before dispatching the webhook to handlers. At minimum, document that `WebhookMetadata#shop` must not be trusted as tenant identity without an independent verification step in the host application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a legitimate, unprivileged action).
2. Shopify sends a genuine webhook to the app: body `B`, header `shopify-hmac-sha256: HMAC(secret, B)`, header `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this `(B, HMAC)` pair (e.g., from their own server logs/proxy).
4. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `shopify-hmac-sha256` header, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes `HMAC(secret, B)` — this still matches, since `shop` was never part of `to_signable_string`.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and any app logic that trusts this field acts on/against the victim tenant using attacker-controlled webhook content.

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
