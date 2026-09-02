### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but `Utils::HmacValidator` only verifies the raw request body against the shared `client_secret`-derived HMAC. The header is never part of the signed data, so any party who can obtain one valid `(body, hmac)` pair for the app (e.g. by installing the app on their own shop and receiving a legitimate webhook) can replay that exact body with a forged `shop-domain` header pointing at a different shop. The HMAC check still passes because it only validates the body bytes, not the claimed shop identity.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header, with no cross-check against the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and compares it to the received `hmac`, never incorporating `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates only this body-only HMAC, then hands `request.shop` straight to the host application's handler as the trusted tenant identifier: [4](#0-3) 

Because a single app's `client_secret` is shared across every shop that installs the app, any merchant/shop that has installed the app can:
1. Receive a legitimate webhook delivery to their own shop, capturing the raw body and its valid `x-shopify-hmac-sha256` value.
2. Replay that exact `(body, hmac)` pair to the app's webhook endpoint, substituting `x-shopify-shop-domain` with a victim shop's domain.
3. `HmacValidator.validate` still succeeds (the body/HMAC pair is genuinely valid for the shared secret), and `Registry.process` dispatches the handler with `shop` set to the forged victim domain.

This breaks the intended binding "shop claimed in the webhook == shop that actually generated/authorized this payload." The identity field acted upon (`shop`, used by the host app to route data into the correct tenant's records) is not covered by the same cryptographic check that authenticates the payload.

### Impact Explanation
This enables cross-tenant data confusion: a low-privilege attacker who merely installs the target app on their own store can inject events/data that the receiving application will attribute to an arbitrary other shop domain, since the gem provides no binding between the authenticated bytes and the claimed shop. Any host application that trusts `WebhookMetadata#shop` (built directly from `request.shop`) as a tenant key — which is exactly what this gem's documented API contract implies — will process attacker-controlled webhook content under another tenant's identity. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires installing the target app on an attacker-controlled shop (the normal free/trial installation flow), which is unprivileged from the perspective of the app's other tenants, and does not require the `client_secret`, an access token, or any credential belonging to the victim shop. The replay is a simple HTTP request forgery once one legitimate webhook has been observed.

### Recommendation
Bind the shop identity to the signed payload before trusting it: include the `shop`, `topic`, and `webhook_id` headers as part of the HMAC-signable string (matching Shopify's inclusion of the shop domain in the signed context) or, alternatively, require host applications to cross-validate `request.shop` against previously stored/authorized shop-token pairs before using it as a tenant key. At minimum, document clearly that `request.shop` is unauthenticated and must not be trusted as a tenant key without additional verification (e.g. checking it against an existing offline `Session` for that shop).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers/receives any webhook (e.g. `orders/create`), capturing the raw JSON body `B` and the header `x-shopify-hmac-sha256: H`, which is valid because `H = HMAC-SHA256(client_secret, B)`.
2. Attacker sends a new POST request to the app's webhook endpoint with the same body `B`, the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and finds it matches `H` — validation succeeds.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and any host application logic keyed on `shop` now processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

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
