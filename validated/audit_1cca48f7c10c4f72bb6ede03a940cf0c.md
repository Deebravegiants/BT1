### Title
Webhook `shop` domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable HMAC payload from the raw request body only, while the `shop` (tenant identity) is read from a separate, unauthenticated HTTP header. `Registry.process` validates only the HMAC-vs-body binding and then hands the unauthenticated `shop` value straight to the host app's webhook handler as the tenant identifier. This breaks the identity binding `shop == authenticated(shop)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (the body) against the provided HMAC — it never inspects `shop`: [3](#0-2) 

`Registry.process` performs this HMAC check and then forwards `request.shop` unauthenticated into `WebhookMetadata`, which is delivered to the app's handler as the tenant identity for the event: [4](#0-3) 

Because the app's `client_secret` (used to compute the HMAC) is shared across *all* shops that have installed the app — not per-shop — any merchant that has installed the app can legitimately trigger a webhook for their own store and obtain a valid `(raw_body, hmac)` pair signed with the app-wide secret. That pair remains valid regardless of which `shop` header accompanies it, because `shop` is excluded from the signed content. The attacker can then resend the same body+HMAC to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` will call the app's handler with `WebhookMetadata.new(shop: <victim-shop>, body: <attacker-controlled-payload>, ...)`.

This is exactly the analog class described by the rules: "a field acted on but not covered by the HMAC" — `shop` is acted upon (used as the tenant key for handler dispatch) but not covered by the signature that is supposed to authenticate the whole request.

### Impact Explanation
Any downstream host application that trusts `WebhookMetadata#shop` (returned by this gem's own `Registry.process`) to select which merchant's session/access token/data to update will process attacker-supplied payloads under a victim shop's identity. This is a cross-tenant integrity violation: a malicious/compromised merchant can inject forged order/customer/inventory events (or any subscribed topic) attributed to any other shop using the same app, using only their own legitimate installation — no `api_secret_key`, access token, or privileged access to the victim required.

### Likelihood Explanation
Medium-to-high: exploitation requires only that the attacker be (or control) any shop that has installed the app and can trigger at least one real webhook of the targeted topic (e.g., placing an order), which is trivial for a normal merchant account. No secret material needs to be obtained — the attacker relies on the fact the signature never covers `shop` in the first place.

### Recommendation
Bind the `shop` header into the signed material verified by `HmacValidator`, or otherwise independently authenticate/attest the shop domain (e.g., cross-check it against the shop that owns the webhook subscription ID before dispatching to handlers) inside `ShopifyAPI::Webhooks::Registry.process`, rather than trusting the unauthenticated `x-shopify-shop-domain` header as the tenant key.

### Proof of Concept
1. App has installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, both sharing the same `client_secret`.
2. Attacker who controls `shop-a` triggers a legitimate event (e.g., `orders/create`), producing a valid `raw_body` and its correct `x-shopify-hmac-sha256` value.
3. Attacker resends the identical `raw_body`/`hmac` to the app's webhook endpoint but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body/HMAC pair (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and the attacker-controlled body, causing the app to act on `shop-b`'s tenant context with forged data.

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
