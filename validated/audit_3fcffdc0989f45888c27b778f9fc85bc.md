### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC over the raw request body only, then dispatches to the app's handler using the `shop` (and `topic`) values taken from HTTP headers that are never included in the signed content. This breaks the intended binding `authenticated_bytes == acted_upon_bytes`: the HMAC proves the body wasn't tampered with, but proves nothing about which shop the body belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read directly from HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`, etc.), which are outside the HMAC's coverage: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` and then hands the header-derived `shop`/`topic` straight to the app's webhook handler as trusted tenant metadata, without any cross-check against the signed body: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the signature only over `verifiable_query.to_signable_string`, i.e. the body, and never over any header value: [4](#0-3) 

This is exactly the report's bug class - "a field acted on but not covered by the HMAC" - and directly parallels the "shnarf vs. state root not bound together" issue: here, the signed artifact (body) and the routing/tenant artifact (`shop-domain` header) are two independently-supplied values that are never cross-validated.

### Impact Explanation
An unprivileged actor who controls any Shopify shop (e.g., a free development store) can register a webhook on their own store, capture the resulting `(body, hmac)` pair - which is validly signed with the app's real `client_secret` because Shopify itself signs it - and replay that exact HTTP request to the victim app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the (unmodified) body against the (unmodified) HMAC; the app's handler then receives `WebhookMetadata` claiming the payload originated from the victim shop. Any app logic that uses `data.shop` to select which tenant's session/store to update (a common and documented usage pattern for this field) will act on the attacker-controlled body under the identity of a different, unrelated shop - a cross-tenant data-confusion/integrity issue reachable without ever knowing the app's `client_secret` or any victim credential.

### Likelihood Explanation
Any developer/merchant account can install the app on their own shop (or use a webhook the app already fires to any shop that installed it) to obtain one valid `(body, hmac)` pair, then simply resend that request with a modified header value using an HTTP client - no secret material, no privileged access, and no interaction with the victim is required. The only prerequisite is reachability of the app's public webhook endpoint, which is inherent to how Shopify webhooks work.

### Recommendation
Bind the header-derived routing fields (`shop`, `topic`, `webhook-id`, `api-version`) into the value that is actually HMAC-verified, e.g. include them in the canonical signed string (similar to how `AuthQuery#to_signable_string` binds `shop`/`host`/`state`/`code` together), or otherwise cryptographically/contextually verify that the `shop-domain` header matches an expected value for the current request context before dispatching to the handler.

### Proof of Concept
1. Register the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic so Shopify sends a legitimately signed request:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over body B>`, body `B`.
2. Capture this request.
3. Replay it to the same app endpoint, only changing the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - Keep body `B` and `x-shopify-hmac-sha256` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)` over `B` only - this still passes.
5. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: JSON.parse(B), ...))` is invoked, so the app processes attacker-supplied content as if it belongs to `victim.myshopify.com`. [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
