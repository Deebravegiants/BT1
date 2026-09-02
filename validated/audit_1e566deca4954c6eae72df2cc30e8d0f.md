### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the shop identity (`shop-domain` header) that is later trusted and forwarded to app webhook handlers is never included in that signed content. Because a single `api_secret_key` is shared across all shops that install the app, any merchant who has installed the app can capture a validly-HMAC'd webhook delivered to their own endpoint and replay it with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop; `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and hand the victim's identity to the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the (unauthenticated) `shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string`, i.e., only the body: [3](#0-2) 

`Registry.process` validates the HMAC, then immediately trusts `request.shop` (and `request.topic`) to construct `WebhookMetadata` passed to the app-defined handler — with no check that `shop` was part of what was signed: [4](#0-3) 

Since Shopify webhook HMACs for an app are computed with the app's single `client_secret` shared across every merchant that installs it, any legitimate (even low-privilege) merchant can obtain a request body + valid HMAC pair addressed to their own shop, then resend that exact body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different (victim) shop. The identity binding broken is:
`shop authenticated by HMAC == shop acted upon by the handler` — the left side is actually "no shop is authenticated by the HMAC at all," while the right side is "whatever the attacker puts in the header."

### Impact Explanation
This is a cross-tenant identity spoofing vector: an app relying on `ShopifyAPI::Webhooks::Registry.process`/`WebhookMetadata#shop` to route webhook effects to the correct tenant (e.g., writing order data, triggering side effects, looking up per-shop session/access tokens) can be made to attribute an attacker-controlled, replayed payload to an arbitrary victim shop known to the attacker, since only the body — not the shop — is authenticated. This matches the Critical-tier "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker (i) install the target app on their own shop (unprivileged, self-service on Shopify) to receive at least one legitimately signed webhook, and (ii) know or guess the victim shop's `.myshopify.com` domain (publicly discoverable). No access to `api_secret_key`, access tokens, or the app's infrastructure is needed — replay is a straightforward HTTP request against the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the HMAC-verified surface: either include the `X-Shopify-Shop-Domain` value as part of `to_signable_string`/verification, or require downstream apps to independently correlate `request.shop` against a known/registered shop record (e.g., existing offline session) before trusting it, and document this gap prominently for consumers of `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, triggering a genuine webhook (e.g., `orders/create`) delivered to the app's webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(client_secret, B)`).
2. Attacker intercepts/logs this raw request (they control the receiving server before it forwards to a shared handler, or they simply resend a captured copy directly to the app's public webhook URL).
3. Attacker resends the identical body `B` and identical `X-Shopify-Hmac-Sha256: H` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only, which still matches `H`, so validation passes.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches it to the app's handler, which now performs shop-scoped work under the wrong tenant's identity.

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
