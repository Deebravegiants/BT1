### Title
Webhook `shop-domain` header is trusted by handlers but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body: `Utils::HmacValidator.validate(request)` calls `validate_signature`, which computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` field. [1](#0-0) [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the tenant-identifying `shop` (and `topic`/`webhook_id`) values are read from HTTP headers (`x-shopify-shop-domain`, etc.) and are never included in the signed material. [3](#0-2) [4](#0-3) 

After the HMAC check passes, `process` builds `WebhookMetadata` directly from these unauthenticated header-derived fields and hands it to the host app's handler as the tenant identity for the event:
`handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))`. [5](#0-4) 

This breaks the intended identity binding `hmac == HMAC(secret, shop || body)`; the gem only enforces `hmac == HMAC(secret, body)`, so `shop` is a field acted on (used to attribute the event to a tenant) but not covered by the HMAC.

### Impact Explanation
Because the `shop` field is unauthenticated, an unprivileged internet user who controls their own Shopify store can subscribe that store to a webhook topic and receive a genuinely, correctly-signed `(body, hmac)` pair from Shopify for their own tenant's data. They can then replay that exact body/HMAC pair to the victim app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (any victim shop domain). Since the gem's `HmacValidator` only checks the body against the HMAC and never binds `shop` into the signature, `Registry.process` will accept the forged request as valid and invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop. If the host application's handler uses `data.shop` to select which merchant record/session/data to update (a standard, gem-documented usage pattern in `docs/usage/webhooks.md`), this enables cross-tenant data corruption/confusion driven entirely from data the gem itself deemed "verified." This matches a Medium/High-severity identity-binding break analogous to the reported bug class (verified bytes not covering the field actually acted upon).

### Likelihood Explanation
Moderate: it requires the attacker to control at least one shop that has the target app installed (or otherwise be able to trigger/capture a legitimately signed webhook body for the target topic), plus knowledge of the target's real shop domain. No access to the app's `client_secret` or access tokens is needed — the attacker only reuses a Shopify-issued signature/body pair they legitimately received for their own store's events.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise require the caller/host app to independently corroborate the `shop-domain` header against a value obtained from a session already known to be authentic (e.g. the endpoint used to receive that shop's webhooks) before trusting `WebhookMetadata#shop`. At minimum, document prominently that `shop-domain` is not covered by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers for topic `orders/create`.
2. Shopify sends a legitimately signed webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays this exact `B` and HMAC to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Webhooks::Request#hmac` and `#to_signable_string` (`lib/shopify_api/webhooks/request.rb:11-38`) only look at the body-derived HMAC header and raw body — both unchanged — so `HmacValidator.validate` returns `true` (`lib/shopify_api/utils/hmac_validator.rb:13-31`).
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, even though this data actually originated from the attacker's own store.

### Citations

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
