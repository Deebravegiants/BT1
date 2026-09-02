## Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values that drive dispatch and are handed to the app's handler as trusted, per-tenant identity are taken directly from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: `lib/shopify_api/webhooks/request.rb:36-38`. [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac-sha256` header using `Context.api_secret_key`: [2](#0-1) 

Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled straight from headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` uses the unauthenticated `topic` header to select the handler and forwards the unauthenticated `shop` header straight into `WebhookMetadata` passed to the app's handler, after only checking that the body's HMAC is valid: [4](#0-3) 

The identity binding that should hold is: `hmac_signature == HMAC(secret, body ∥ shop ∥ topic)`. Instead it only holds `hmac_signature == HMAC(secret, body)`, i.e. `shop` and `topic` are values "acted on but not covered by the HMAC."

Because the API secret key is shared across all shops that install the same app (it is the app's `client_secret`, not a per-shop secret), any merchant that installs the app can legitimately trigger Shopify to send the app a webhook with a validly-signed body for their own shop. That attacker-controlled tenant can capture a real `(raw_body, hmac)` pair from a webhook Shopify sent for their own store, then replay the exact same body and HMAC value to the app's webhook endpoint while altering the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a victim shop. `HmacValidator.validate` will still succeed because it never inspected those headers, and `Registry.process` will invoke the handler believing the event legitimately originates "from" the victim shop.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-acted-upon binding and results in cross-tenant confusion: a handler that persists or acts on webhook data keyed by `WebhookMetadata#shop` (e.g., updating that shop's local order/customer/product record, triggering per-shop side effects) can be made to attribute attacker-supplied body content to an arbitrary victim shop domain, since the shop identity is asserted by an unauthenticated header rather than being cryptographically bound to the signed payload.

### Likelihood Explanation
Any developer/merchant who can install the same app (a normal, unprivileged action) can obtain one valid `(body, hmac)` pair for their own store and then freely resend it with a forged `shop-domain`/`topic` header to the app's public webhook endpoint — no access token, secret, or privileged account is required beyond running the app on a store they control.

### Recommendation
Include the `shop`, `topic`, and `webhook_id`/`api_version` header values in the signable string that is HMAC-verified (or otherwise cryptographically bind them to the raw body, e.g. by validating the headers as part of the HMAC input as Shopify's webhook envelope allows), so an attacker cannot swap these headers on a validly-signed body without invalidating the signature.

### Proof of Concept
1. App developer installs their own copy of the app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, body `B`, and `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker resends the same body `B` and same `hmac-sha256` value to the endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) validates successfully because it only checks `B` against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered `orders/create` handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and attacker-controlled body `B`, even though this data never originated from Shopify on behalf of `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
