### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (tenant identity) is read from the unauthenticated `X-Shopify-Shop-Domain` / `Shopify-Shop-Domain` HTTP header. `Utils::HmacValidator.validate` only verifies the raw body bytes against the HMAC, never the shop header, so the shop identity used by webhook handlers is not bound to the signature that authenticates the request.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) [2](#0-1) 

`to_signable_string` returns `@raw_body` only — the `shop` value (derived from the `shop-domain` header) is not part of the bytes that get HMAC-verified. `Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string`: [3](#0-2) 

`Registry.process` calls `HmacValidator.validate(request)` and, once it passes, trusts `request.shop` (and `request.topic`) to dispatch to the handler as the tenant identity: [4](#0-3) 

Because the app's webhook secret (`api_secret_key`) is shared across every shop that installs the app (it is not shop-specific), any merchant who has legitimately installed the app — an ordinary, unprivileged user with no special access to any other tenant — can capture a genuinely-signed webhook delivered to their own endpoint (body + `hmac-sha256` header) and simply resend it with the `shop-domain` header changed to point at a different shop. The HMAC signature will still validate, since the shop identity was never part of the signed content, and `Registry.process` will hand the (attacker-supplied) `body` to the handler tagged with an arbitrary victim `shop`: [5](#0-4) 

This breaks the identity binding `shop verified == shop acted on`: the shop that is cryptographically authenticated (implicitly, via the shared secret used to sign the body) is not the shop that ends up being used to identify the tenant for the handler's business logic.

### Impact Explanation
Any application built on this gem that uses `request.shop` from `WebhookMetadata` to select/update a specific tenant's records (which is the documented, expected usage pattern) can be made to process attacker-controlled webhook bodies under an arbitrary victim shop's identity. Depending on the handler, this enables cross-tenant data corruption/injection (e.g., an `orders/create` or `app/uninstalled` payload attacker controls being attributed to a shop the attacker does not own), which matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (unprivileged) installer of the app on their own shop, receive one real webhook (which happens automatically once an app is installed and any subscribed event occurs), and replay it with a modified header — no possession of `api_secret_key`, access tokens, or any victim credentials is required. This is a straightforward, repeatable attack path for any external developer who installs the app once.

### Recommendation
Include the shop identity (and other identity-relevant fields such as topic/api_version, if used for handler dispatch) inside the HMAC-signed payload verification, or independently verify that the `shop-domain` header corresponds to a shop the app has an active/expected session or installation record for before dispatching to the handler. At minimum, `to_signable_string` should not be the sole basis for trusting `request.shop`; the gem should document/enforce that consumers must cross-check `shop` against their own installation records rather than treat it as authenticated purely because the HMAC passed.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook to the app's endpoint with headers `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and a JSON body.
2. Attacker captures this raw body and its valid HMAC (no secret needed — they just observed a webhook Shopify sent them).
3. Attacker resends the identical body + HMAC to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the (unchanged) raw body against the HMAC — validation succeeds.
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's body, as shown in the dispatch code: [4](#0-3) .

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
