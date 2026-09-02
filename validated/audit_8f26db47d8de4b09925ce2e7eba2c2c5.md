This confirms the vulnerability: `WebhookMetadata.shop` is passed directly from the unauthenticated `x-shopify-shop-domain` header to the handler, while the HMAC (`Utils::HmacValidator.validate(request)`) only ever signs `request.to_signable_string`, which returns `@raw_body` alone. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop-domain identity spoofing via HMAC that only covers the raw body, not the `shop` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` value that is subsequently handed to the app's handler and used to identify the tenant is read from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, which is never included in the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [4](#0-3)  and `Request#shop` is read straight from an HTTP header with no cryptographic binding to that body: [5](#0-4) .

`Registry.process` validates only the HMAC-over-body before dispatching to the app's handler with the header-derived shop: [2](#0-1) .

Because the same `api_secret_key` is shared across every shop that installs the app, and because `HmacValidator.validate` only checks `computed_signature == received hmac` over the body bytes (`OpenSSL.secure_compare(computed_signature, T.must(received_signature))`) [6](#0-5) , any attacker who installs the app on a shop they control receives genuine `(raw_body, hmac)` pairs signed with the app's real secret. The attacker can capture one such valid pair (attacker fully controls the JSON payload content available to legitimate webhook topics they can trigger, e.g. `orders/create`, `customers/create`, etc.) and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed because it never inspects the `shop` header, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` field claims to be the victim tenant while the `body` is entirely attacker-authored: [3](#0-2) .

This is the same identity-binding class described in the analog report: a value that is *acted upon* (here, the tenant/shop identity used to route and persist webhook data) is not covered by the authenticity check (the HMAC), so an attacker can decouple the two and impersonate another tenant.

### Impact Explanation
Any host application that trusts `WebhookMetadata#shop` (returned by this gem as the authenticated tenant identifier) to select which merchant's records to create, update, or delete will process attacker-authored data under another merchant's identity. This is a cross-tenant data injection / spoofing primitive directly enabled by this gem's webhook verification API, meeting the High bar of "cross-tenant access" via a documented library primitive that host apps are expected to trust as authenticated.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be able to install the target app on any shop (including a free/dev store they control) to legitimately trigger webhook deliveries with attacker-chosen body content, and (2) the ability to POST an HTTP request to the app's public webhook endpoint with forged headers, which is trivial for an unprivileged internet user with no special access, credentials, or timing constraints.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise verify the header-provided shop against a shop known to have installed the app (e.g., cross-check `request.shop` against a stored, previously-authenticated session/shop record) before dispatching to the handler, rather than treating `Request#shop` as authenticated purely because the body's HMAC validated.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a store they own).
2. Attacker triggers a webhook event (e.g. creates an order) whose JSON body content they fully control/know in advance.
3. Shopify delivers the webhook to the app's endpoint with headers `x-shopify-hmac-sha256: <valid_hmac_for_body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and the raw body `B`.
4. Attacker captures `(B, valid_hmac_for_B)` and replays it directly to the same endpoint, replacing the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `B` only, which matches `valid_hmac_for_B`, so validation succeeds.
6. `ShopifyAPI::Webhooks::Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled B>, ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
