### Title
Webhook shop attribution is not covered by HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (tenant identity) for a webhook exclusively from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, while `ShopifyAPI::Utils::HmacValidator.validate` only verifies the HMAC over the raw request body. The shop field is therefore a "field acted on but not covered by the HMAC," breaking the equality `shop authenticated == shop bound by signature`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which computes the signature over `to_signable_string`: [2](#0-1) 

`to_signable_string` returns only `@raw_body` — it never includes the `shop` value. Yet `shop` is read straight from the (attacker-controllable) header and passed unverified into the handler payload: [3](#0-2) [1](#0-0) 

Contrast this with the OAuth callback `AuthQuery`, where `shop` **is** part of the signed payload (`to_signable_string` includes `shop:`), correctly binding shop identity to the HMAC: [4](#0-3) 

For webhooks, however, the app's webhook-signing secret (`Context.api_secret_key`, the app's `client_secret`) is shared across *all* shops that install the app — it is not shop-specific. Consequently, any merchant/tenant that has installed the app can legitimately receive a webhook for their own shop, capture the valid `X-Shopify-Hmac-Sha256` value (computed only from body bytes), and replay that exact body + valid HMAC to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header pointing at a victim shop. Because `shop` is never part of the signed content, `Registry.process` will accept the forged request as valid and pass `shop: <victim-shop>` to the registered handler.

### Impact Explanation
Downstream handlers key data storage/side-effects on `WebhookMetadata#shop` (e.g., updating shop-specific records, triggering per-shop business logic). Since the shop identity is unauthenticated relative to the signature, a low-privileged actor (any shop that installed the app) can inject webhook payloads that the app attributes to a different, victim tenant — a cross-tenant data/action confusion. This matches the in-scope "cross-tenant access" impact.

### Likelihood Explanation
Any merchant who has installed the app can trivially obtain one valid `(body, hmac)` pair from their own legitimate webhook traffic (no secret leakage or privileged access required), then replay it against the shared public webhook endpoint with a modified shop header. No credentials, tokens, or the app's `client_secret` need to be obtained by the attacker — likelihood is high for any app that trusts `request.shop`/`WebhookMetadata#shop` in handler logic.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed/verified payload, or otherwise cryptographically bind the shop header to the HMAC-verified body — e.g., verify that `shop` matches an expected/previously-registered shop for the topic, or incorporate the header into the signable string before comparing HMACs, matching the approach already used in `Auth::Oauth::AuthQuery#to_signable_string`.

### Proof of Concept
1. Shop A installs the app and legitimately receives an `orders/create` webhook with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker (owner/operator of shop A) intercepts this and resends a POST to the app's public webhook endpoint with:
   - `raw_body = B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(client_secret, B) == H`. [5](#0-4) 
4. `request.shop` returns `"victim-shop.myshopify.com"` and this value is forwarded to the app's handler as authenticated data for that shop. [6](#0-5)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
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
