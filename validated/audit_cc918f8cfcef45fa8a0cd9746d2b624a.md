This confirms the vulnerability: the HMAC in `ShopifyAPI::Webhooks::Request` is computed only over the raw body (`to_signable_string` returns `@raw_body`), while `shop` is read from the separate, unsigned `shopify-shop-domain`/`x-shopify-shop-domain` header, and `Registry.process` passes that header value straight into the `WebhookMetadata` handed to the app's handler without any cross-check against the signed payload.

### Title
Webhook tenant identity (`shop`) is not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC solely against that signable string using the app's `api_secret_key` [2](#0-1) . The `shop` value, however, is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header [3](#0-2) , which is not part of the signed content at all. `Registry.process` validates only the HMAC over the body and then forwards `request.shop` unchanged into `WebhookMetadata`, which is delivered to the app's handler as the tenant identifier: [4](#0-3) .

Because the `api_secret_key` (the app's `client_secret`) is identical for every shop that installs the app, any merchant/tenant who has installed the app can legitimately receive genuine, validly-signed webhook deliveries for their own store. Since the signature never binds `shop`, that attacker-controlled tenant can replay the exact same raw body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop` value in the `shopify-shop-domain` header. `HmacValidator.validate` will still pass because the signature check only examines `@raw_body`, and the forged `request.shop` will be trusted as the acting tenant for that webhook body — breaking the identity binding: `shop authenticated by HMAC` ≠ `shop value the app actually acts on`.

### Impact Explanation
This crosses a tenant boundary: a low-privilege attacker (any merchant who can install the app and thus receive one legitimately signed webhook) can make the app process/store data under a victim shop's identity, since the only tenant field (`shop`) passed to the handler is unauthenticated. Depending on how the host application keys per-tenant storage from `data.shop` (as documented in `docs/usage/webhooks.md` and `BREAKING_CHANGES_FOR_V15.md`), this enables cross-tenant data injection/corruption — a Critical-class outcome per the scope rules.

### Likelihood Explanation
Exploitation requires no secrets beyond what any app-installing merchant already has access to (their own genuine webhook deliveries). The attacker only needs to capture one raw webhook body + its valid `hmac-sha256` header for their own shop, then POST it to the app's public webhook endpoint with a rewritten `shop-domain` header — a purely unprivileged, internet-reachable action. Likelihood is high wherever a host app trusts `WebhookMetadata#shop` for tenant scoping, which is the documented, expected usage pattern of this gem.

### Recommendation
Include the shop domain (and ideally other identity-relevant headers such as `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified — e.g., bind `to_signable_string` to a canonical combination of the trusted headers plus the body, or independently verify that the `shop` header corresponds to a shop known to have installed the app before trusting it. At minimum, document that `WebhookMetadata#shop` is not itself authenticated and must not be used as the sole tenant key without additional verification (e.g., cross-referencing against the topic/webhook_id recorded at registration time for that specific shop).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering Shopify to send a real webhook (e.g. `orders/create`) to the app's registered endpoint, signed with the app's `api_secret_key` over the exact raw JSON body.
2. Attacker captures the raw body `B` and the corresponding `X-Shopify-Hmac-Sha256` header value `H` from that legitimate delivery (trivial — it's a request sent to infrastructure they control, e.g., their own webhook proxy/logging).
3. Attacker replays an HTTP POST directly to the app's public webhook route with:
   - Body: `B` (unmodified)
   - Header `X-Shopify-Hmac-Sha256: H` (unmodified)
   - Header `X-Shopify-Shop-Domain: victim.myshopify.com` (forged, targeting a different tenant)
   - Header `X-Shopify-Topic`: same topic as captured
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `HMAC(api_secret_key, B)` [5](#0-4) .
5. `request.shop` returns the forged `victim.myshopify.com` [3](#0-2) , and the app's handler receives `WebhookMetadata` claiming this data belongs to `victim.myshopify.com`, even though the body content actually originated from the attacker's own shop.

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
