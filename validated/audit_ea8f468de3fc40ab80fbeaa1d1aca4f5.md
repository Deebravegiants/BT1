### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` (from the `X-Shopify-Shop-Domain` header) as the tenant identifier passed to webhook handlers, but the HMAC verification performed by `ShopifyAPI::Utils::HmacValidator` only signs/verifies the raw request body — never the shop header. Any attacker who can obtain one genuinely-signed webhook (e.g. by installing the target app on their own store) can replay that exact body/HMAC pair while substituting the `shop-domain` header for a victim shop, and the gem will accept it as valid and dispatch it as if it came from the victim shop.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is read directly from a header that is not part of the signed content: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC strictly against `to_signable_string` (the body), independent of any header value: [3](#0-2) 

`Registry.process` performs only this body-HMAC check, then trusts `request.shop` verbatim and forwards it to the app's handler as the tenant identity: [4](#0-3) 

Because the shop domain is never part of the signed bytes, the binding "HMAC-verified request == request attributed to `shop`" does not hold: `verified_bytes(body) ≠ verified_bytes(body) ∧ shop`. An attacker who legitimately installs the app on a shop they control (an ordinary, unprivileged self-service action — no `api_secret_key`, access token, or privileged account needed) will receive real webhooks with a valid HMAC computed only over the body. They can then replay that identical body+HMAC to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header to an arbitrary victim shop domain. `HmacValidator.validate` still succeeds (it never inspects the header), and `Registry.process` calls the handler with `WebhookMetadata.new(..., shop: request.shop, ...)` claiming the victim's identity.

### Impact Explanation
This breaks the shop/tenant authentication boundary: the app-level handler (which typically uses `shop` to look up/update per-merchant records, credentials, or state) receives attacker-controlled data falsely attributed to a shop the attacker does not control. Depending on how the consuming app uses webhook `shop` values (common pattern: keying database writes, triggering per-shop side effects, or updating cached settings), this enables cross-tenant data corruption/injection — a Critical-tier "cross-tenant access" outcome per the scope's impact categories.

### Likelihood Explanation
Likelihood is high: the only prerequisite is the ability to install the target app on a store the attacker controls, which is normal, unprivileged self-service behavior for any public/embedded Shopify app. No secrets, tokens, or social engineering are required — the attacker uses their own legitimately-issued webhook payload and simply changes an unauthenticated header before replay.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed content, or otherwise cryptographically bind the header claims to the verified body — e.g., require the caller to additionally verify `request.shop` against a known/installed shop list, or extend `to_signable_string` so the signature covers `shop + raw_body` rather than the body alone.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`.
2. Capture a genuine webhook delivery: headers include `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body against the HMAC — validation succeeds.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process attacker-supplied data as if it originated from the victim shop.

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
