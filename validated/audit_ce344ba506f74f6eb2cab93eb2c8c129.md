## Title
Webhook shop-domain identity spoofing due to HMAC not covering the `shop` field - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`Webhooks::Registry.process` authenticates a webhook only by validating the HMAC over the raw request body, but the `shop` (tenant identity) that the payload is routed and attributed to is read from an unauthenticated HTTP header and never covered by that HMAC. This breaks the identity binding `authenticated_bytes == claimed_shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed string: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `to_signable_string` (the body) and secure-compares it to the `hmac` value, never touching the `shop` field: [3](#0-2) 

`Registry.process` uses this same unauthenticated `request.shop` value to build the `WebhookMetadata` that is handed to the app's handler as the identity of the tenant the payload belongs to, right after the HMAC check that never validated it: [4](#0-3) 

Because Shopify apps typically use one shared `api_secret_key` for all installed shops, any valid `(raw_body, hmac)` pair authenticated for one tenant remains cryptographically valid regardless of which shop's domain is attached to it. An attacker who possesses one authentic `(raw_body, hmac)` pair (e.g., from their own installed/trial shop) can resubmit that exact body and HMAC to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. `HmacValidator.validate` still returns `true` (the body/HMAC pair is untouched), and `Registry.process` will dispatch the payload to the handler labeled with the attacker-chosen victim shop, i.e. the identity `shop authenticated by HMAC` != `shop used to route/persist the data`.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to guarantee: the gem authenticates *that a webhook payload came from Shopify using the shared secret*, but the host application (following this gem's documented API) is led to believe `WebhookMetadata#shop` is equally authenticated, when it is not. An attacker can inject or overwrite data under an arbitrary victim shop's identity, meeting the Critical bar for cross-tenant access.

### Likelihood Explanation
The webhook endpoint is intentionally public/unauthenticated apart from HMAC verification, and the `shop-domain` header is fully attacker-controlled at the HTTP layer. Any actor who has ever received (or can generate, e.g. via their own installed shop) one authentic `(body, hmac)` pair for the shared app secret can replay it with an arbitrary shop header value; no privileged credentials, TLS interception, or access-token possession by the attacker is required.

### Recommendation
Bind the tenant identity into the authenticated material: either include the `shop-domain` header value in the HMAC-signed string (mirroring how `AuthQuery#to_signable_string` includes `shop`), or, before dispatching to the handler, cross-check `request.shop` against the shop associated with the specific `webhook_id`/topic registration recorded by the app, rejecting mismatches.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (unprivileged, ordinary merchant).
2. Attacker triggers a real webhook (e.g. `orders/create`) and obtains its exact `raw_body` and the corresponding `x-shopify-hmac-sha256` value delivered by Shopify (both valid under the app's shared `api_secret_key`).
3. Attacker sends a POST to the app's public webhook endpoint reusing that identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) passes because it only checks the body/HMAC pair.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the application to process/store attacker-supplied data under the victim tenant's identity.

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
