Confirmed vulnerability: the webhook `shop` binding is broken because the HMAC only signs the raw body, not the `shop-domain` header.

### Title
Webhook shop attribution is not covered by HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `#shop` is read directly from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . `Registry.process` validates the HMAC over the body only and then dispatches to the app's handler using `request.shop` taken from that unsigned header [3](#0-2) . This mirrors the reported bug class: a field (`shop`) that is acted upon (used to attribute the webhook to a tenant) is not covered by the integrity check (the HMAC signable string).

### Finding Description
The binding that should hold is: `shop-domain header == shop that the HMAC-signed payload actually originated from`. In this implementation, `HmacValidator.validate(request)` computes `HMAC(secret, request.to_signable_string)` and compares it against `request.hmac` (from the `hmac-sha256` header) [4](#0-3) . Since `to_signable_string` is just the raw JSON body, the HMAC proves only "this body byte sequence was produced by Shopify with this app's secret" — it says nothing about which shop the header claims sent it. Any party capable of intercepting or replaying a legitimately signed webhook body for Shop A (e.g., a malicious or compromised HTTP intermediary, a misconfigured proxy, or an attacker who can influence header propagation into the app, such as another tenant hosted behind the same shared ingress) can resend that same signed body while substituting the `shopify-shop-domain` header value for Shop B. `HmacValidator.validate` will still pass because it never inspects `shop`, and `Registry.process` will hand the (Shop A's) payload to Shop B's tenant context via `WebhookMetadata.new(... shop: request.shop ...)` [5](#0-4) .

Before the fix: `shop` (used for tenant dispatch) ≠ any field inside the HMAC-covered signable string.
After a correct fix: `shop` must be part of `to_signable_string` (or otherwise cryptographically bound), so `HMAC-verified shop == dispatched shop`.

### Impact Explanation
This breaks the tenant identity binding for webhook processing: an app relying solely on this gem's `Registry.process`/`Request` for webhook shop attribution can be made to process a cross-tenant payload under the wrong shop identity, i.e., attacker-controlled or replayed data attributed to a victim shop, or vice versa — a cross-tenant data integrity issue. This aligns with the report's root cause pattern (data acted upon that is not covered by the authenticity check), even though the concrete exploitation path (header manipulation) requires the app's networking layer to expose header trust to an attacker.

### Likelihood Explanation
Moderate/contextual: exploitability depends on whether the deploying environment allows an attacker to control or replay the `shop-domain` header independently of the signed body (e.g., through a shared load balancer, header injection, or a captured legitimate webhook request replayed with a modified header). The gem itself provides no defense — it only checks the header's presence, never its integrity — so the guarantee it documents ("HMAC validates the webhook") is weaker than assumed for the `shop` field specifically.

### Recommendation
Include `shop` (and ideally `topic`) in the HMAC-covered signable string, or independently verify that `request.shop` matches an expected/allow-listed value tied to the session under which the webhook was registered, before dispatching to `handler.handle`. At minimum, document that `shop-domain`/`topic` headers are not authenticated by `HmacValidator.validate` so integrators add their own binding check.

### Proof of Concept
1. Capture a legitimately Shopify-signed webhook request for `shop-a.myshopify.com` (valid `X-Shopify-Hmac-Sha256` over the raw body).
2. Resend the identical raw body and HMAC header, but with `X-Shopify-Shop-Domain` changed to `shop-b.myshopify.com`.
3. Call `ShopifyAPI::Webhooks::Registry.process(request)`; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` [1](#0-0) , and the handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` while the actual signed payload originated from `shop-a` [6](#0-5) .

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
