### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant shop spoofing via header injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity used to route and process a webhook exclusively from the unauthenticated `shop-domain` HTTP header, while its `to_signable_string` method — the material verified by `Utils::HmacValidator` — covers only the raw request body. This is the same class of bug described in the external report: a field that is *acted upon* (the shop the webhook is attributed to) is not part of the data that is *cryptographically bound* by the integrity check (the HMAC). Just as the analog rules describe ("a shop authenticated versus the shop stored as a session key"), the shop that is authenticated by HMAC (none — the shop is never in the signed material) diverges from the shop that is later trusted to build `WebhookMetadata` and dispatch to the app's per-shop handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` is read straight from the `shop-domain` header with no relation to the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` only ever inspects `verifiable_query.to_signable_string` (i.e., the body) and `verifiable_query.hmac`: [4](#0-3) 

The binding that should hold is:
`shop bound by HMAC == shop delivered to WebhookHandler#handle`

but the actual code enforces only:
`HMAC(secret, body) == received_hmac` **and separately** `shop = header["shop-domain"]` (unauthenticated)

Because the header is never part of `to_signable_string`, an attacker who legitimately installs the app on their own shop (or otherwise obtains one genuinely-signed webhook payload/body+HMAC pair for a shop they control) can replay that same raw body and valid HMAC to the app's shared webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header value naming a different, victim shop. The HMAC check passes (it never looked at the header), and `WebhookMetadata#shop` is populated with the attacker-chosen victim shop domain, which the host application will use to route/attribute the event.

### Impact Explanation
This crosses a tenant boundary: it lets a user (attacker) with a genuine app installation on their own store forge a webhook that a shared multi-tenant app will process as if it came from a different merchant's store. Depending on the topic handled (e.g., `app/uninstalled`, `shop/update`, `customers/redact`, order/fulfillment topics), a host application relying on `WebhookMetadata#shop` for merchant attribution can have its per-tenant state corrupted, be tricked into revoking/deleting another merchant's data, or misassociate order/customer data across tenants — a cross-tenant access/data-integrity impact, matching the "Critical – cross-tenant access" category in the rules. No access token, refresh token, `client_secret`, or TLS interception is required — only a legitimate (even free) install of the target app on an attacker-controlled shop to obtain one valid signed webhook body.

### Likelihood Explanation
Moderate-to-high. Any developer/attacker can install a public or free-to-install Shopify app, trigger any webhook topic on their own store to capture a body + valid `X-Shopify-Hmac-Sha256`, and then POST that same body/HMAC pair to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header. Nothing in `ShopifyAPI::Webhooks::Request` or `Registry.process` prevents this because the shop header is structurally outside the HMAC's coverage.

### Recommendation
Bind the shop identity to the verified material instead of trusting the header in isolation:
- Include the `shop-domain` header (and ideally `topic`/`webhook-id`) in the HMAC-covered `to_signable_string`, or
- Require the host application to independently confirm that `request.shop` corresponds to a shop with an active, previously-established session/installation before dispatching to `WebhookHandler#handle`, and document this requirement prominently, or
- At minimum, cross-check the `shop-domain` header against a shop that is expected to be able to produce the given signed body (e.g., per-shop or per-install secret verification is not applicable here since Shopify uses a single app secret, so the safest fix is signing the header value itself as part of `to_signable_string`).

### Proof of Concept
1. Attacker installs the target multi-tenant app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook topic (e.g. `app/uninstalled`) on their own shop, capturing the raw POST body `B` and the corresponding valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify with the app's real `client_secret`, which the attacker never needs to know).
3. Attacker sends a new HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it signs `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, B) == H`. [5](#0-4) 
5. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and passed to the app's `WebhookHandler#handle`, which the host application trusts as the authenticated tenant for this event.

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
