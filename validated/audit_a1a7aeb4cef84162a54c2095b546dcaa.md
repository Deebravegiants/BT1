### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable value from the raw request body only, while the `shop` (and `topic`/`webhook-id`) values are taken from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC against the body but then trusts the header-derived `shop` value as the tenant identity passed to the app's handler, without that value being covered by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate`, which in turn only checks `verifiable_query.to_signable_string` (the raw body) against `verifiable_query.hmac`: [3](#0-2) 

After this body-only check passes, `Registry.process` builds `WebhookMetadata` using `request.shop` as the authoritative tenant identity and dispatches it to the host application's handler: [4](#0-3) 

The identity binding that should hold is: `shop-header == shop-bound-by-hmac`. In this implementation, `to_signable_string` (the bytes actually verified) never includes the `shop` header, so the equality is broken — the HMAC only proves "this body byte-sequence was produced with the app's secret," not "this body was produced for this shop." Since a single Shopify app uses one `client_secret`/`api_secret_key` across all shops that install it, any shop with the app installed can legitimately receive a validly-HMAC-signed webhook body. That attacker-controlled shop can capture a genuine `(raw_body, hmac)` pair delivered to it, then replay the identical body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspected the shop header, and `Registry.process` forwards the forged `shop` value to the handler as if it were authentic.

### Impact Explanation
This breaks the tenant boundary the app relies on to route/scoping webhook side effects (e.g., updating shop records, revoking access on `app/uninstalled`, processing customer data requests) per shop. An attacker who controls one shop with the app installed can cause the host application to process attacker-supplied webhook data under a victim shop's identity — a cross-tenant access/confusion condition satisfying the Critical severity bar (cross-tenant access) defined for this scan.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-controlled development/trial shop (a normal, low-privilege action), (2) triggering any webhook topic the app has registered to obtain a valid `(raw_body, hmac)` pair, and (3) POSTing that same body/HMAC to the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, access tokens, or TLS interception is required, and the endpoint is by design internet-reachable and unauthenticated aside from HMAC verification.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook-id`, `api-version`) header values in the bytes that are HMAC-verified, or otherwise cryptographically bind the shop domain to the signed payload (e.g., verify the shop domain against a pre-registered/expected value tied to the delivery, not solely from an attacker-controllable header) before it is treated as trusted metadata in `WebhookMetadata`.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook delivery (e.g., `orders/create`) and capture the raw POST body `B` and header `x-shopify-hmac-sha256: H` sent by Shopify (both are valid because they're signed with the app's single `api_secret_key`).
3. Replay to the app's webhook endpoint:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim.myshopify.com
x-shopify-webhook-id: <any>
x-shopify-api-version: <any>

B
```
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `B` against `H`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches `WebhookMetadata` with `shop: "victim.myshopify.com"` to the app's handler, even though the body content originated from the attacker's own shop.

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
