### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and exposes an HMAC that authenticates only the raw request body, while the `shop` (and `topic`, `api-version`, `webhook-id`) values are read directly from unauthenticated HTTP headers and then handed to the app's webhook handler as trusted identifiers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate`/`validate_signature` compute and compare the HMAC exclusively against that signable string [2](#0-1) . Meanwhile, `Request#shop` simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or its HMAC [3](#0-2) . `Registry.process` validates only the body's HMAC via `Utils::HmacValidator.validate(request)`, then dispatches to the handler passing `request.shop` as the trusted tenant identifier without any additional check that the header matches the shop that actually produced/owns the signed body [4](#0-3) .

The binding that should hold is:
`shop_bound_by_hmac == shop_used_for_tenant_routing`

but the code only enforces `hmac_valid_for(raw_body)`, independent of `shop`. This breaks the equality: the `shop` header used to route/attribute webhook data to a specific merchant tenant is not the same value that the HMAC actually authenticates.

### Impact Explanation
Any actor capable of submitting an HTTP request to the app's webhook endpoint with a body + HMAC pair that is valid for *any* shop (e.g., replaying/observing a legitimately-received webhook for their own installed shop, since HMAC uses the app's shared `client_secret` and is the same for all shops of that app) can freely substitute the `shop-domain` header to point at a different, victim shop. Because `Registry.process` and `WebhookMetadata` trust `request.shop` for tenant attribution without it being covered by the signature, this enables cross-tenant data confusion: an app that persists or acts on webhook data keyed by `data.shop` could apply attacker-supplied data (from a shop the attacker controls) to a different tenant's records, or misattribute events across merchants — a cross-tenant impact.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and one legitimately-signed webhook payload (which merchants who install the app naturally receive, since the HMAC is computed with the app's shared secret and is not shop-specific). No access to `api_secret_key`, access tokens, or privileged accounts is required — only rewriting an unauthenticated header.

### Recommendation
Include the `shop` (and ideally `topic`, `api-version`, `webhook-id`) values in the HMAC-signable content, or otherwise cryptographically bind the shop header to the payload before trusting it for tenant routing. At minimum, cross-validate `request.shop` against an expected/allow-listed shop associated with the specific installation context before using it to key any stored data or handler logic.

### Proof of Concept
1. App receives a genuine Shopify webhook for `attacker-shop.myshopify.com` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends a request to the app's webhook endpoint with the same body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` succeeds because it only checks `HMAC(client_secret, B) == H`, which is still true [5](#0-4) .
4. `Registry.process` calls the handler with `WebhookMetadata` built from `request.shop == "victim-shop.myshopify.com"` and the attacker-controlled body, even though the payload never came from Shopify for that shop [4](#0-3) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
