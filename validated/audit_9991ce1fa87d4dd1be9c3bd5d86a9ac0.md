### Title
Webhook shop identity is not bound to the HMAC signature, allowing shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then passes the `shop` value taken from the unauthenticated `x-shopify-shop-domain` (or `shopify-shop-domain`) header straight to the handler as the trusted tenant identifier. Because the HMAC signature never covers that header, any party who can produce one valid `(body, hmac)` pair — which any merchant with the app installed can trivially do by triggering a real webhook on their own store — can replay that pair while swapping the shop-domain header to name a different (victim) shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the signature purely against that signable string, i.e. purely against the body: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof of the entire request's authenticity and then forwards `request.shop` (sourced from the unauthenticated header) to the app's handler as the identity of the shop the event belongs to: [3](#0-2) [4](#0-3) 

The identity binding broken is: `shop authenticated by HMAC == shop used as the tenant key delivered to the handler`. In reality, the HMAC only proves "the body bytes were signed by Shopify's shared app secret for *some* shop," while `shop`, `topic`, `webhook_id`, and `api_version` are read from headers that are completely outside the signed material.

### Impact Explanation
Any user who can get one legitimate webhook delivered to the app (e.g., by installing the app on their own store and triggering an event) obtains a valid `(raw_body, hmac)` pair. They can replay this exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and `WebhookMetadata.shop` will report the victim's shop to the host application's handler. Any host-application logic that keys per-tenant data, triggers side effects (e.g., data sync, uninstall/GDPR cleanup, order processing) off `WebhookMetadata#shop` can now be made to act on/for a shop the attacker does not own, corrupting cross-tenant state — the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the ability to generate one real webhook from any shop (installing the app is a normal, unprivileged action for any Shopify merchant/dev-store owner) and the ability to POST an HTTP request with attacker-controlled headers to the app's public webhook endpoint — no access to the app's `api_secret_key`, access tokens, or victim credentials is required.

### Recommendation
Bind the shop identity to the signed payload rather than trusting the header: e.g., include the shop domain in the signable string used for HMAC validation, or require the webhook handler to validate `request.shop` against an application-level allowlist/registration record for that topic instead of trusting the header unconditionally. At minimum, document that `WebhookMetadata#shop`/`topic`/`webhook_id` are not authenticated by the HMAC and must not be used as a sole tenant-authorization key.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify sent.
2. Attacker POSTs to the app's webhook endpoint with headers `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: victim.myshopify.com`, and body `B`.
3. `Registry.process` calls `HmacValidator.validate(request)`, which only checks `H` against `HMAC(secret, B)` — this passes because `B` and `H` are unmodified.
4. `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` is delivered to the app's handler, which now believes attacker-controlled event data originated from `victim.myshopify.com`.

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
