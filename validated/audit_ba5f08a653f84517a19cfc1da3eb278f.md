This confirms the vulnerability. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` in `Webhooks::Registry.process` only authenticates the raw body bytes, never the `shop`, `topic`, `api_version`, or `webhook_id` values, all of which are read directly from HTTP headers [2](#0-1) . Those unauthenticated header-derived values are then passed straight into the handler as trusted identity fields [3](#0-2) .

### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values — which are read from HTTP headers and passed to the app's webhook handler as trusted identity fields — are never included in the signed payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it (via `secure_compare`) to the `hmac-sha256` header: [4](#0-3) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from unauthenticated headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts these header-derived fields to route and identify the tenant: [3](#0-2) 

The identity binding that should hold is: `shop/topic/webhook_id authenticated == shop/topic/webhook_id acted on`. Because only the body bytes are HMAC-protected, this equality does not hold. Any party who can obtain one valid `(raw_body, hmac)` pair for *any* topic/shop (e.g., by installing the app on their own store and receiving a legitimate webhook, which is an ordinary, unprivileged action available to any merchant/developer) can replay that exact body and HMAC to the app's webhook endpoint while substituting arbitrary values for `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version`. The HMAC check still passes because it only verifies the body was signed by the app's secret at some point — it says nothing about which shop or topic that body was signed for.

### Impact Explanation
This breaks the tenant/topic identity binding that webhook handlers rely on: a handler written to trust `WebhookMetadata#shop`/`#topic` (e.g., to look up and mutate per-shop state, redeliver data, or make authorization decisions) can be made to act on attacker-chosen shop/topic values while presenting a body the attacker fully controls the origin of. This is a cross-tenant data-integrity/impersonation issue in a multi-tenant SaaS context — an attacker can make the app process webhook data under the identity of a shop they do not control.

### Likelihood Explanation
Exploitation only requires the ability to send arbitrary HTTP requests to the app's public webhook endpoint plus one previously-observed valid `(body, hmac)` pair, which is trivially obtainable by installing the app on any test/dev store (a normal, unprivileged action) and capturing the resulting webhook delivery. No access to `api_secret_key` or any credentials is required.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (or otherwise cryptographically bind them to the body, e.g., by using Shopify's per-shop webhook signing where available), and reject requests where recomputed values don't match. At minimum, the library should not expose header-derived shop/topic values as trusted output of a "validated" webhook without documenting that host applications must independently corroborate `shop` against the caller's known/expected tenant.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery, capturing the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `HMAC(secret, B) == H`).
2. Attacker sends a new POST request to the app's webhook endpoint with the same body `B` and header `H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or any topic registered by the app)
   - `X-Shopify-Webhook-Id: <arbitrary>`
3. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(secret, B) == H`, which still holds.
4. `Registry.process` dispatches to the handler for the attacker-chosen topic with `shop: "victim-shop.myshopify.com"`, even though this webhook was never actually sent by Shopify for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
