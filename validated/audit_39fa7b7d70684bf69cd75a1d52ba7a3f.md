### Title
Webhook `shop`/`topic` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` reads the shop domain, topic, webhook id, and API version straight out of unauthenticated HTTP headers, while the HMAC that `ShopifyAPI::Webhooks::Registry.process` relies on to "authenticate" the webhook only covers the raw request body. This breaks the identity binding `shop_header == shop_that_produced_this_signed_body`, letting anyone who can obtain one validly-signed webhook body (e.g. from their own shop) replay it to the app while claiming it originated from a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only the raw body bytes: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are parsed straight from headers with no cryptographic tie to the signed payload: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e. the body) using `Context.api_secret_key`: [3](#0-2) 

`Registry.process` uses that body-only HMAC as its sole authenticity check, then immediately dispatches the handler using the unauthenticated `request.shop` and `request.topic` header values: [4](#0-3) 

The equality the code implicitly assumes is:
`hmac_valid(raw_body) == true` implies `request.shop == the_shop_that_actually_sent_this_body`

But the HMAC only proves `raw_body_bytes == bytes_signed_by_secret`; it says nothing about the `shop-domain`/`topic`/`webhook-id` headers, which are attacker-controlled on any HTTP request the attacker sends to the app's public webhook endpoint.

### Impact Explanation
Because `WebhookMetadata` (and therefore the app's topic handler) receives `shop: request.shop` straight from the header while the cryptographic check only vouches for the body, an attacker who can produce or capture one legitimately HMAC-signed body (trivially available: sign up as a merchant/dev-store owner, install the app, and let Shopify send the app a real, validly-signed webhook for the attacker's own store) can resend that exact body to the app's endpoint with the `X-Shopify-Shop-Domain` (and/or topic) header changed to a victim shop. The HMAC still validates because it never covered those headers, so `Registry.process` will invoke the handler believing the payload came from the victim tenant. Any handler that uses `data.shop` to select which merchant's session/access token/data to act on (the pattern the library itself documents via `WebhookMetadata`) will act on attacker-controlled content mislabeled as belonging to another tenant — a cross-tenant confusion/injection matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitability only requires the ability to send arbitrary HTTP requests to the app's (typically public) webhook endpoint and to have obtained one validly-signed body — achievable by any unprivileged internet user who can install the target app on a shop they control (a normal, unprivileged Shopify action), no `api_secret_key`, access token, or privileged account needed. The signable-string design that omits headers is intrinsic to `Request#to_signable_string`/`HmacValidator`, so every consumer of `Registry.process` is affected identically.

### Recommendation
Do not let downstream handlers trust the unauthenticated `shop`/`topic`/`webhook_id` header values as tenant identity. At minimum, `Registry.process`/`Request` should cross-check that the shop domain used to look up a merchant's session/access token is independently re-derived (e.g., by looking up the shop's stored offline session via `webhook_id`/topic uniqueness constraints already enforced server-side, or by validating the header-derived shop against Shopify's callback/webhook subscription records) rather than trusting `x-shopify-shop-domain` merely because the body's HMAC checked out. If feasible, incorporate the header values into the signable string or otherwise cryptographically bind them before dispatch.

### Proof of Concept
1. Install the target app on an attacker-owned development store `attacker.myshopify.com` and subscribe to a webhook topic (e.g. `orders/create`).
2. Capture the resulting webhook HTTP request sent by Shopify to the app: raw body `B`, headers including `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
3. Resend the identical body `B` and HMAC header `H` to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H`, so `ShopifyAPI::Webhooks::Registry.process` passes validation at [5](#0-4)  and calls the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker-authored body content, even though `victim-shop.myshopify.com` never sent this data.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
