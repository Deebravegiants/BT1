Confirmed: the webhook HMAC only signs `raw_body` (`to_signable_string` returns `@raw_body`), while `topic`, `shop`, `api_version`, and `webhook_id` are taken from HTTP headers that are never part of the signed material. `Registry.process` verifies only the HMAC over the body and then forwards `request.shop` unchanged to the handler as the tenant identifier.

### Title
Webhook `shop` (and topic/id) identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator` verifies the HMAC exclusively against that body [1](#0-0) [2](#0-1) . However, `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are read straight from HTTP headers that are not covered by that signature at all [3](#0-2) . `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build `WebhookMetadata` passed to the handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop-domain header == the tenant the HMAC-signed body actually originated from`. Because the HMAC only covers `@raw_body`, this equality is never enforced by the gem. Any HTTP request whose body+HMAC pair is valid for the app's secret will pass `Utils::HmacValidator.validate` regardless of what `shopify-shop-domain` (or `x-shopify-shop-domain`) header accompanies it [5](#0-4) .

An unprivileged internet user who can obtain even one legitimately-signed webhook body+HMAC pair for the app (e.g., by installing the app on their own store and capturing/replaying webhooks Shopify sends them) can resubmit that exact body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a different, victim merchant's domain. `Registry.process` will consider the HMAC valid (it only checks the body) and hand the handler a `WebhookMetadata` object whose `shop` is the attacker-chosen value [6](#0-5) . If the app's handler keys any state, record association, or authorization decision on `data.shop` (which is the documented/intended use of this field), the attacker can inject data attributed to another tenant — a cross-tenant integrity/confusion issue, not merely a body-replay concern for a single tenant.

This is analogous to the audited "field acted on but not covered by the HMAC" class of bug: `writeTuple`'s `idx` byte controlled where a value was written but wasn't masked/bound correctly to the intended slot; here, the `shop` byte-string controls which tenant a payload is attributed to but is never bound into the value that is HMAC-verified.

### Impact Explanation
This breaks the tenant-identity binding `verified-shop == body-signing-shop`, letting an attacker with only their own (or any) app installation forge the shop attribution of an otherwise-valid webhook delivery. Depending on how the host application's `WebhookHandler#handle` implementation consumes `data.shop` (e.g., to look up or mutate merchant-scoped records), this can lead to cross-tenant data corruption or disclosure — classified as High under the cross-tenant access impact criteria.

### Likelihood Explanation
Any app developer using this gem's webhook handling (`ShopifyAPI::Webhooks::Registry.process`) as documented is exposed, since the gem itself never validates that the `shop` header matches the tenant the signature was generated for. An attacker only needs one legitimately-signed body/HMAC pair (trivially obtainable by installing the app themselves, since HMAC is app-secret-wide, not shop-specific) and the ability to send an HTTP request with custom headers to the app's public webhook endpoint — no `api_secret_key`, access token, or privileged access is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically/contextually verify that the shop asserted in headers matches the shop the signature was actually generated for (e.g., include shop in `to_signable_string`, or require the caller to supply/verify an expected shop before trusting `data.shop`). At minimum, document prominently that `request.shop` is unauthenticated and must be independently corroborated (e.g., against a known/registered shop) before being used for any tenant-scoped action.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for the app secret), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the identical request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H`, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `B` only and finds it matches `H`, so validation succeeds [5](#0-4) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: parsed_body(B), ...)`, causing the host app to process attacker-supplied data as if it came from `victim.myshopify.com` [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L36-38)
```ruby
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L27-31)
```ruby
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
