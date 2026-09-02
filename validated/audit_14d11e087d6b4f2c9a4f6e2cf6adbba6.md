### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) fields are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop`, `topic`, `webhook_id`, and `api_version` HTTP headers — none of which are covered by that HMAC — straight through to the app's webhook handler as trusted metadata.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header: [2](#0-1) 

Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read verbatim from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`), with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` validates only the HMAC and then constructs `WebhookMetadata` directly from these unauthenticated header values, passing `shop: request.shop` to the app's handler as if it were an authenticated identity: [4](#0-3) 

The identity binding the library implicitly promises to the host application (and that the docs describe as "verify the request did indeed come from Shopify") is: `shop_asserted_in_metadata == shop_covered_by_hmac`. In reality the equality is:

`shop_asserted_in_metadata (from header, attacker-controlled)` ≠ `bytes_verified_by_hmac (raw_body only)`

Any party that can obtain one genuine, HMAC-signed webhook body from Shopify (e.g., an attacker who installs the app on their own shop and triggers a webhook-eligible event) can replay that exact raw body to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `topic`/`webhook-id`) for a different tenant's domain. `HmacValidator.validate` still returns `true` because it only checks the untouched raw body against the (secret-derived) signature — it never re-derives or checks the shop/topic headers.

### Impact Explanation
This breaks tenant isolation for any application that uses `ShopifyAPI::Webhooks::Registry.process`/`WebhookMetadata#shop` to route webhook data or perform shop-scoped actions (e.g., store/update per-shop database records, trigger per-shop side effects) trusting that `shop` was authenticated by "did Shopify sign this." An attacker controlling one shop can cause the app to process a cross-tenant/spoofed webhook attributed to an arbitrary victim shop domain, which the docs explicitly describe as validated ("verify the request did indeed come from Shopify"): [5](#0-4) 
This falls under cross-tenant access impact.

### Likelihood Explanation
Likelihood requires the attacker to possess at least one legitimately-signed webhook body (achievable by installing the app on their own store and triggering any registered webhook topic — no privileged credentials or `api_secret_key` needed), then replaying it with a modified `shop-domain` (and optionally `topic`/`webhook-id`) header to the same public webhook endpoint. This is realistic for any unprivileged internet user/merchant who can install the target app.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable payload validated by `HmacValidator`, or otherwise cryptographically bind these header values to the signed body before trusting them in `WebhookMetadata`. At minimum, document that host applications must independently verify `request.shop` against their own installed-shop registry rather than relying on `Registry.process`'s HMAC check to authenticate the shop identity.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event (e.g., `orders/create`) to receive a genuine webhook POST with valid `X-Shopify-Hmac-Sha256` computed over the raw JSON body.
2. Replay the exact same raw body and HMAC header to the app's webhook route, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and adjust `X-Shopify-Topic`/`X-Shopify-Webhook-Id` as desired).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — the forged `shop-domain` header passes unchecked: [6](#0-5) 
4. The app's registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes it as an authenticated event for the victim tenant.

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
