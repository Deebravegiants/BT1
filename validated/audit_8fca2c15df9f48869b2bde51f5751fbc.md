### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook purely by validating the HMAC over the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values that the host application relies on to identify the tenant are read straight from unauthenticated HTTP headers that are never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that signable string [2](#0-1) . Meanwhile `Request#shop` (and `#topic`, `#webhook_id`, `#api_version`) are read directly from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header via `shopify_header`, a value that is never mixed into the HMAC computation [3](#0-2) .

`Registry.process` validates only the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` that is handed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `hmac_valid(raw_body) == true` implies `shop header == shop that produced raw_body`. In this implementation that equality does not hold — the header is orthogonal to the signed payload. Any request whose body was legitimately signed by Shopify for one shop (e.g. a webhook delivered to an app installed on the attacker's own store) remains HMAC-valid if the attacker (who controls the HTTP request being replayed to the app's public webhook endpoint) changes only the `shop-domain` header to name a different, victim shop. `Registry.process` will still call `Utils::HmacValidator.validate(request)` successfully (because it only checks `raw_body`) and will pass the attacker-chosen `shop` string straight into the handler as trusted tenant identity.

### Impact Explanation
This breaks the cross-tenant boundary: the value the host application relies on for tenant attribution (`request.shop`, exposed via `WebhookMetadata#shop`) is not cryptographically bound to the authenticated payload. A host application that uses this `shop` value to select a session, write records, or trigger tenant-scoped side effects (a documented, expected usage of `WebhookMetadata`) can be made to act on data under an attacker-chosen shop identity while the signature check reports success, i.e., cross-tenant access facilitated by the gem's own webhook verification primitive.

### Likelihood Explanation
Exploitation requires the attacker to possess one validly HMAC-signed webhook body for any topic (trivially obtainable by installing the same app on their own store and receiving a legitimate webhook), plus the ability to replay/POST a crafted HTTP request with a different `shop-domain` header to the app's public webhook endpoint. No secret material, access token, or privileged account for the victim shop is required, only network access to the app's already-public webhook receiver.

### Recommendation
Bind the tenant identity into the verified material instead of trusting a bare header: incorporate `shop`, `topic`, and `webhook_id` into the signable string/HMAC computation (or independently verify the shop domain against Shopify's known/registered set for this app, e.g., cross-check with `Context` state or a session lookup) before constructing `WebhookMetadata`, so that `hmac_valid` can only be true for the exact `shop` that Shopify actually signed the payload for.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic so Shopify delivers a legitimately HMAC-signed request (`raw_body`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker.myshopify.com`) to the app's webhook endpoint.
2. Capture that request. Re-send it to the same endpoint, changing only the `x-shopify-shop-domain` header to `victim.myshopify.com`, keeping `raw_body` and `x-shopify-hmac-sha256` untouched.
3. `Utils::HmacValidator.validate(request)` (called from `Registry.process`) recomputes the HMAC over `raw_body` only and matches, per [5](#0-4) .
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim.myshopify.com"` [6](#0-5) , causing the host application's handler to process attacker-controlled data as belonging to the victim tenant.

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
