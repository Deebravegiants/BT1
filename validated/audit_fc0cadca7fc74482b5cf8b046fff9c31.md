### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers and then trusted by `ShopifyAPI::Webhooks::Registry.process` to build the tenant context passed to the app's handler. Because the shop identity is never bound to the HMAC that is actually verified, a party who can obtain one valid `(body, hmac)` pair for the shared app secret can replay it with a forged `shop-domain` header and make the app believe the event originated from a different (victim) merchant.

### Finding Description
`Utils::HmacValidator.validate` verifies `request.hmac` against a signature computed solely from `request.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled from headers that are entirely attacker-controlled at the HTTP layer and are never included in the signable string: [3](#0-2) 

`Registry.process` only checks that the HMAC (on body only) is valid, then forwards `request.shop` — the unauthenticated header value — as the tenant identity to the app's webhook handler: [4](#0-3) 

The binding that should hold is: `shop header used for tenant routing == shop that produced/authorized this signed payload`. Because the HMAC only binds the body (not shop/topic/id), that equality is never actually checked — any request with a body+hmac pair valid for the app's shared secret can carry an arbitrary `shop-domain` header.

### Impact Explanation
The `api_secret_key` used to compute/verify the HMAC is shared by the app across **all** installed shops (it is the app's client secret, not a per-shop secret). A single malicious merchant who installs the app can receive genuine Shopify webhooks for their own store — real `(body, hmac)` pairs that pass `HmacValidator.validate`. They can then replay that exact body/HMAC to the app's public webhook endpoint while swapping only the `X-Shopify-Shop-Domain` header to a victim shop's domain. `Registry.process` will validate successfully (the HMAC only covers the body) and dispatch the handler with `shop: <victim-shop>`, causing the host application to act on/modify data attributed to a shop the attacker does not own — a cross-tenant integrity violation attributable directly to this gem's webhook verification logic, not merely "the host app ignoring documentation."

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even trial/free) installer of the target app — a low bar for any public Shopify app — and the ability to send an arbitrary HTTP POST with custom headers to the app's public webhook endpoint, both of which are realistic for an "unprivileged internet user" relative to other merchants' tenants.

### Recommendation
Bind the tenant/topic identity into the verified signature material, or otherwise cryptographically tie the `shop-domain` (and ideally `topic`, `webhook-id`) header to the payload before trusting it — e.g., include these headers in `to_signable_string`, or validate `request.shop` against a shop known to be associated with a currently valid session/access token for this app before invoking the handler, rather than trusting the header outright.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, triggering a real webhook (e.g. `orders/create`) signed by Shopify with the app's shared secret.
2. Attacker captures the raw body `B` and the `X-Shopify-Hmac-Sha256` header `H` from that delivery (`H` is valid for `B` under `HmacValidator.validate`, since verification only checks `to_signable_string == B`, see `lib/shopify_api/webhooks/request.rb:35-38`).
3. Attacker POSTs to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body's HMAC (`lib/shopify_api/webhooks/registry.rb:188-190`).
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-supplied data as if it came from `victim-shop`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
