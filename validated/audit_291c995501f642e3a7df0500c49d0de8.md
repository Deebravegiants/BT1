## Title
Webhook `shop` domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop` (tenant identifier) that gets handed to the application's webhook handler is read straight from the `X-Shopify-Shop-Domain` header, which is never part of the signed material. An attacker who controls one legitimately-signed webhook (from their own store) can therefore replay it with a forged shop-domain header and have the app process it as belonging to a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The `shop` accessor, however, is read from a header that is completely outside that signed string: [2](#0-1) [3](#0-2) 

`Registry.process` validates the request purely through `Utils::HmacValidator.validate(request)` (which only checks the body-derived signature) and then forwards `request.shop`, taken from the unauthenticated header, directly into the data passed to the app's handler: [4](#0-3) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e., the body for webhooks, and never incorporates the shop header: [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding failure: the binding that should hold is `shop_header == shop_that_produced_the_signed_body`, but the code only checks `hmac(body) == hmac_header`. The shop header can be swapped freely without breaking HMAC validation, because it isn't part of the signed input.

### Impact Explanation
Any application that keys tenant-scoped logic (session/access-token lookup, billing state, uninstall handling, order/customer records, etc.) off `WebhookMetadata#shop` as supplied by this gem is exposed to cross-tenant data confusion: an attacker owning any single shop that has this app installed can produce a validly-signed webhook body for their own shop, then re-send it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `x-shopify-shop-domain`) header changed to a victim shop's domain. `Registry.process` will accept it (HMAC only checks the body) and dispatch it to the handler tagged as coming from the victim shop, achieving cross-tenant impact within the app.

### Likelihood Explanation
The attacker needs no secrets beyond having their own shop install the app (a normal, unprivileged flow) in order to obtain one validly HMAC-signed webhook body/hmac pair. Swapping an HTTP header to reach the app's public webhook endpoint requires no special access. Since `Registry.process` never cross-checks the header shop against any value bound to the HMAC, the forged request passes validation deterministically.

### Recommendation
Bind the shop identity into the value that is HMAC-verified, or otherwise cryptographically tie `request.shop` to the signed payload before it is trusted, e.g., include the shop domain in `to_signable_string`, or require callers/handlers to independently corroborate `shop` (for instance by verifying it against a shop that is already known/authorized for that specific webhook subscription) rather than trusting the raw header value once the body-only HMAC check passes.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook (e.g., `orders/create`) with body `B`, and Shopify-computed header `X-Shopify-Hmac-Sha256: H` (valid for secret `S` and body `B`).
2. Attacker resends the exact same body `B` and same `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds regardless of the shop header.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body(B), ...)` and invokes the app's handler with data falsely attributed to `victim-shop.myshopify.com`, even though `victim-shop` never sent this webhook.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
