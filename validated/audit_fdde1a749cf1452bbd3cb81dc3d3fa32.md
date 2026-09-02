### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the `shop-domain` header — the value used to attribute the webhook to a specific merchant/tenant — is never included in the signed bytes. This breaks the binding `shop_attributed_to_webhook == shop_that_Shopify_actually_signed_for`, allowing an attacker who possesses one validly-signed webhook body (e.g., from their own store) to replay it against the app while swapping the `shop-domain` header to a victim shop, resulting in cross-tenant data/webhook confusion.

### Finding Description
`Request#to_signable_string` returns only the raw body, never the headers: [1](#0-0) 

The `shop` accessor, however, is read straight from the (uncovered) header: [2](#0-1) 

`HmacValidator.validate` computes and compares the signature purely against `to_signable_string`, i.e. the body, with no header material mixed in: [3](#0-2) 

`Registry.process` gates on this HMAC check, then immediately trusts `request.shop` (the unauthenticated header) to build the `WebhookMetadata` dispatched to the app's handler: [4](#0-3) 

Because the shop identity is carried out-of-band from the signed payload, `(body, hmac)` pairs are shop-agnostic: any request with a body/HMAC pair that was validly generated for shop A will also pass validation when replayed with the `shop-domain` header rewritten to shop B. The gem's own test fixtures demonstrate that the HMAC is computed from the body alone, independent of the `shop` value used in the header: [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity-binding failure: the gem attributes an authenticated webhook payload to whatever shop domain the caller supplies in an unauthenticated header. Any consuming app that uses `WebhookMetadata#shop` to key per-tenant data (session lookups, install/uninstall state, redact/data-request processing, order records, etc.) can have that data attributed to, or acted on for, the wrong merchant. Given a genuine app installation on any shop, an attacker can capture their own legitimately-signed webhook deliveries and replay them under a different shop's identity, causing cross-tenant data injection/corruption — this matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs to be a legitimate merchant with the app installed on one shop (unprivileged relative to any other tenant) to obtain a validly HMAC-signed `(body, hmac)` pair for arbitrary webhook topics they control the content of (e.g., via normal store activity that triggers a webhook). No access to `client_secret` or `api_secret_key` is required — the HMAC value is simply copied verbatim from a real delivery. Replaying it against the app's public webhook endpoint with a modified `shop-domain` header is trivial and requires only standard HTTP tooling.

### Recommendation
Include the shop identity (and other identity-relevant headers such as `api-version`, `webhook-id`, `topic`) in the signable string used for HMAC verification, or otherwise cryptographically bind the `shop-domain` header to the signed payload before `Registry.process` uses it to route/attribute webhook data. At minimum, document that consuming applications must not trust `WebhookMetadata#shop` unless it is independently corroborated (e.g., cross-checked against a shop already known from a prior, properly authenticated OAuth/session flow) rather than relying on the HMAC check alone to guarantee the header's authenticity.

### Proof of Concept
1. App is installed on Shop A. Trigger any webhook topic (e.g., `orders/create`) so Shopify delivers a payload with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: shop-a.myshopify.com`, and body `B`.
2. Attacker (merchant of Shop A, or anyone who can observe/capture this delivery, e.g. via their own webhook forwarding proxy) records `(B, H)`.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a different, victim tenant that also has the app installed).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this succeeds because the signature never covered the shop header: [6](#0-5) 
5. The app's registered handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and the attacker-supplied body `B`, causing Shop A's webhook payload to be processed/stored as if it belonged to Shop B.

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

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
```
