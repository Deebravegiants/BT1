## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unsigned `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while the HMAC signature that `Registry.process` validates only covers the raw request body. Anyone who can obtain one valid `(body, hmac)` pair — which any internet user can do simply by installing the app on their own store and receiving a genuine webhook — can replay that pair to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop, and the signature will still validate.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Webhooks::Request#shop` is read straight from the caller-supplied, unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC over that same raw body and then hands the request straight to the topic handler using `request.shop`, with no cross-check that the shop is the one the signature was actually produced for: [3](#0-2) 

The broken identity binding is:
`shop_used_by_handler (WebhookMetadata.shop, from unsigned header) == shop_bound_by_signature (none — HMAC covers only body, no shop claim)`

Since the HMAC is computed only over the JSON body with the app's `api_secret_key`, and the same `api_secret_key` is shared across every shop that installs the app, a valid `(body, hmac)` pair generated for tenant A's webhook is equally "valid" when replayed with tenant B's `shop-domain` header — the signature check in `HmacValidator.validate` has no dependency on the shop field at all: [4](#0-3) 

### Impact Explanation
This breaks tenant isolation (cross-tenant access), matching the required "Critical - cross-tenant access" category. An attacker who installs the app on a shop they control (no privileged credentials needed — installing a public app is an unprivileged action) receives genuinely signed webhooks for their own shop. They can then resend that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, causing the handler to process attacker-controlled webhook data as though it originated from a different, victim tenant. Any application logic that trusts `WebhookMetadata#shop` to look up/update per-shop state (the intended and documented use, per `test/webhooks/registry_test.rb`) can be corrupted or confused this way.

### Likelihood Explanation
Likelihood is high: no secret material is required, only the ability to install the app on any store (an action available to any internet user for public apps) and the ability to POST to the app's public webhook endpoint with custom headers, which is exactly what the library's documented header-parsing logic accepts.

### Recommendation
Include the shop domain (and ideally the API version) as part of the signable content, or otherwise cryptographically bind the tenant to the signature — Shopify itself already signs webhook headers via HMAC in some contexts. At minimum, `Webhooks::Registry.process`/handlers should verify that `request.shop` matches a shop for which the topic/webhook subscription is actually known/registered before dispatching, rather than trusting the header value implicitly.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com`.
2. Trigger a webhook (e.g. `orders/create`) and capture the raw body and the `x-shopify-hmac-sha256` header Shopify sends — both are valid per `HmacValidator.validate`.
3. Replay the exact same body and HMAC header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Webhooks::Request#hmac`/`#shop` parse independently; `HmacValidator.validate` still returns `true` since it only checks the body signature, per: [5](#0-4) 
5. `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"`, letting the attacker inject data attributed to a shop they do not control.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
