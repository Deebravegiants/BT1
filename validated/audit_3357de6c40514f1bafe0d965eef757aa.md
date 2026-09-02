# Webhook Tenant Spoofing via Unauthenticated `shop` Header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request **body**, but the `shop` (tenant) identity it hands to the app's handler is read from an HTTP header that is never included in that HMAC computation. This breaks the intended binding `hmac_verified_bytes == identity_used_for_tenant_routing`, allowing a request with a genuinely-signed body (obtainable by any merchant who installs the app on their own store) to be replayed against the public webhook endpoint with a forged `shop` header, causing the app to process attacker-controlled webhook data under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

Meanwhile, `Request#shop` is read directly from an HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`) with no cryptographic tie to the HMAC-covered body: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards `request.shop` (the unauthenticated header) as the tenant identity to the application's webhook handler: [4](#0-3) 

The equality this code implicitly (and incorrectly) assumes is:
`bytes covered by HMAC (raw_body) == bytes that determine tenant identity (shop header)`

In reality these are disjoint: the body's HMAC is computed with the app's single `api_secret_key`, which is shared across *every* shop that has the app installed — it is not shop-specific. Any merchant can install the app on their own store, trigger an action that causes Shopify to deliver a legitimately HMAC-signed webhook to the app's public endpoint, capture that exact `(body, hmac)` pair (it is their own traffic), and then POST the same body/hmac pair directly to the app's endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because the body is unchanged, and `Registry.process` will invoke the handler believing the webhook belongs to the victim shop.

### Impact Explanation
This crosses the tenant boundary the library is meant to protect via `WebhookMetadata#shop`: an unprivileged internet user (any merchant capable of installing the app) can inject attacker-chosen webhook payloads (order/customer/product data, cancellation events, etc., subject to whichever topics the app subscribes to) that the host application will process and persist as if they originated from a different, victim shop. Depending on how the host application uses `WebhookMetadata#shop`/`#body` (e.g., to look up/update per-shop records), this can lead to cross-tenant data corruption, spoofed business events, or triggering of shop-specific side effects (e.g., fulfillment, notifications, billing logic) for a shop the attacker does not control. This satisfies the "cross-tenant access" criterion for a Critical-impact analog of the reported bug class (an identity/authorization field consumed without being bound to the verified authentication material).

### Likelihood Explanation
The prerequisite—installing the app on one's own store to obtain a validly-signed webhook body/hmac pair—is trivial and requires no privileged access, credentials, or social engineering; it is the normal, unprivileged installation flow available to any internet user. Capturing one's own webhook traffic and replaying it with a modified header against the same public endpoint requires only basic HTTP tooling.

### Recommendation
Do not trust the `shop`/`x-shopify-shop-domain` header as the sole source of tenant identity for a webhook. Either:
1. Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material used for verification (e.g., derive/verify the shop from signed body content rather than headers), or
2. Cross-check the header-derived shop against a shop value embedded in, and covered by, the signed payload before dispatching to handlers, rejecting mismatches.

At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used by host applications as an authoritative tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and performs an action that fires a webhook the app has registered for (e.g., `orders/create`).
2. Shopify delivers the webhook to the app's public endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, and the JSON body.
3. Attacker records the exact `body` and `x-shopify-hmac-sha256` value (their own traffic).
4. Attacker sends a new POST request directly to the same public webhook endpoint with the identical `body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) succeeds because it only checks `raw_body` against the HMAC — the shop header is irrelevant to the check.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, causing the application to process attacker data as belonging to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
