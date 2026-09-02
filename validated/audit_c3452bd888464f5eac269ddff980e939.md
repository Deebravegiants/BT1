### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The external report's root cause is that `Executor.execute()` acts on a value (native token transfer) that is not actually validated/receivable by the destination, i.e., a mismatch between what is transferred/trusted and what is checked. The closest analog in this Ruby gem is in webhook processing: `ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the **raw body**, then trusts the `shop` (tenant identity) taken from an **unsigned header** and passes it straight to the app's handler as authenticated metadata.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `request.shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header with no cryptographic binding to that value [2](#0-1) .

`Registry.process` verifies authenticity using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. only the raw body) and HMACs it with the app's `api_secret_key` [3](#0-2) . After this check passes, `Registry.process` immediately constructs `WebhookMetadata` using `request.shop` — the unsigned header — and hands it to the app's `WebhookHandler#handle` as the trusted tenant identity [4](#0-3) .

This is the identity-binding break requested: the field **acted upon** (the `shop` used to route/attribute the webhook to a tenant) is not the field **covered by the HMAC** (only the raw body bytes are signed). Formally, the code implicitly assumes:
```
HMAC_valid(raw_body) == HMAC_valid(shop_header)
```
but only the left side is ever checked; the right side is never checked. `WebhookMetadata.shop` [5](#0-4)  is populated straight from that unverified header and passed to the host app, which typically uses it to look up the tenant's session/store record for further action (per `docs/usage/webhooks.md` usage pattern).

### Impact Explanation
If an attacker who has ever observed one legitimate webhook delivery (e.g. from their own store, a store they control, or one intercepted in transit/logs) can replay the exact same raw body while substituting the `shop-domain` header for a victim shop, `Registry.process` will pass HMAC validation (since only the body bytes are hashed) and deliver the payload to the app's handler tagged with the victim's shop domain. Depending on how the host app trusts `WebhookMetadata#shop` (e.g., to select which merchant's DB record/session to mutate), this enables cross-tenant data confusion/write — one of the accepted "Critical: cross-tenant access" outcomes, without requiring the attacker to know the app's `api_secret_key`.

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain at least one valid `(raw_body, hmac)` pair (from any shop, including their own test store, since HMAC uses a static per-app secret shared across all merchants) and being able to deliver an HTTP POST to the app's webhook endpoint with an attacker-chosen `shop-domain` header alongside the replayed body/HMAC. Because Shopify signs the same way for every shop with the app's single `api_secret_key`, any legitimate webhook the attacker can trigger for their own store (a normal, low-privilege capability of installing the app on a store they control) yields a body+HMAC pair that remains valid when replayed with a different `shop-domain` header. This makes the likelihood high for apps that install on multiple/untrusted merchants and trust `WebhookMetadata#shop` for tenant routing.

### Recommendation
Bind the shop identity into the material that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the request: 
- Have `Request#to_signable_string` (or a new verification step) include the `shop-domain` header alongside the raw body, matching the pattern already used for OAuth (`AuthQuery#to_signable_string` includes `shop` in the signed payload) [6](#0-5) .
- Alternatively/additionally, require the host application to cross-check `WebhookMetadata#shop` against a shop already known/authorized for the webhook `topic`/subscription before acting on it, and document this requirement clearly, since the gem currently offers no guarantee that `shop` is authenticated.

### Proof of Concept
1. Install the app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to and capture the raw POST body and its `x-shopify-hmac-sha256` header value (both are attacker-visible since the attacker owns that shop).
2. Send a new POST to the app's webhook endpoint with:
   - Same raw body bytes and same `x-shopify-hmac-sha256` value captured in step 1.
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (or any other target tenant domain).
   - `x-shopify-topic` matching a registered handler.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate`, which recomputes HMAC over `@raw_body` only [1](#0-0)  — validation succeeds because the body/HMAC pair is unmodified.
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the spoofed `shop-domain` header and invokes the app handler with `shop: "victim-shop.myshopify.com"` [7](#0-6) , even though the request never proved any relationship to that shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
