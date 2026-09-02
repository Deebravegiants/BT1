Confirmed. The webhook HMAC signature only covers the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` identity used by `Registry.process` for tenant dispatch is read directly from an unauthenticated header — never mixed into the signed bytes.

### Title
Webhook `shop` (Tenant) Identity Is Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `Utils::HmacValidator.validate` verifies solely that the *body bytes* were signed by Shopify with the app's `client_secret`. However, `Registry.process` uses `request.shop`, which is read straight out of the `x-shopify-shop-domain`/`shopify-shop-domain` header — a value that is never part of the signed payload. [1](#0-0) [2](#0-1) 

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(client_secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the request. For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body`. [3](#0-2) [4](#0-3) 

The `shop`, `topic`, `api_version`, and `webhook_id` values are all pulled from HTTP headers via `shopify_header`, none of which are included in the HMAC-signed bytes. [5](#0-4) 

`Registry.process` validates the HMAC and, on success, unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the app's handler — the value used by the host application to determine *which merchant/tenant* the payload belongs to: [2](#0-1) 

The broken identity binding, as an equality that should hold but doesn't:
`shop used for HMAC verification == shop used for tenant dispatch (WebhookMetadata#shop)`

In reality the HMAC only binds `raw_body`, so `shop` (and `topic`/`webhook_id`) can be freely substituted by anyone who can produce one valid `(raw_body, hmac)` pair signed with the same `client_secret` — which any unprivileged party can obtain by installing the target app on their own free/dev store and capturing a real webhook delivery for that store. They can then replay that exact body+hmac pair to the victim app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to an arbitrary victim shop domain. `HmacValidator.validate` still succeeds (it only checks the body), and the handler receives `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This breaks the tenant boundary that HMAC verification is supposed to enforce: an unprivileged attacker who is a legitimate (but unrelated) app installer can forge webhook events "from" any other merchant's shop domain, because the shop field the host application relies on for per-tenant processing is never authenticated. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to update per-shop settings, mark uninstalls, process `customers/redact`/`shop/redact` compliance topics, or trigger shop-scoped business logic), this is a cross-tenant data integrity/confusion vector — the impact category explicitly listed as Critical (cross-tenant access) in scope for this analysis.

### Likelihood Explanation
Requires only: (1) installing the target app on an attacker-controlled store to legitimately receive one real webhook with a valid HMAC (no privileged credentials, no access token or `client_secret` needed), and (2) replaying that body/HMAC pair to the target's webhook endpoint with a modified `shop` header. No knowledge of `client_secret` is required since the attacker never needs to forge a new signature — they reuse a validly-signed body while only changing headers that were never covered by the signature.

### Proof of Concept
1. Attacker installs the victim app on their own store `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, e.g. for topic `orders/create`, capturing `raw_body` and the resulting `x-shopify-hmac-sha256` header (both validly signed by the shared `client_secret`).
2. Attacker sends a new HTTP request to the app's webhook endpoint using the **same** `raw_body` and `x-shopify-hmac-sha256`, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic` unchanged (or any registered topic, since it's also unauthenticated)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-computes HMAC over `raw_body` — validation passes. [6](#0-5) 
4. `request.shop` returns the forged header value `victim-shop.myshopify.com`, and the handler is invoked with `WebhookMetadata` asserting the event originated from the victim's shop, even though it never did. [7](#0-6) 

### Recommendation
Bind the tenant-identifying and dispatch-relevant fields (`shop`, `topic`, and ideally `webhook_id`) into the HMAC-signed material, or otherwise cryptographically bind headers to the body (e.g., by validating the `shop` returned matches a shop known to have an active registration/session created via legitimate OAuth for that specific webhook subscription) before trusting `request.shop` for any tenant-scoped action.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
