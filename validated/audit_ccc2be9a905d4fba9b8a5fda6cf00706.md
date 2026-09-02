## Finding

The gem's webhook processing binds its HMAC signature only to the raw request body, but attributes the webhook to a `shop` value taken from an unauthenticated header. This breaks the equality that should hold: `bytes_verified_by_hmac == bytes_the_app_attributes_the_event_to`.

### Title
Webhook Shop-Domain Spoofing via HMAC Not Covering Tenant Identity - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, excluding the `shop` (i.e., `x-shopify-shop-domain`/`shopify-shop-domain` header). `HmacValidator.validate` therefore only proves that the body bytes were signed with the app's secret — it proves nothing about which shop the header claims to be. `Registry.process` accepts the HMAC as sufficient authorization and then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata`, which host apps use to attribute the payload to a tenant. [1](#0-0) [2](#0-1) 

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it to the `hmac` header value: [3](#0-2) 

For webhooks, `to_signable_string` is defined as just the raw body: [4](#0-3) 

`shop` is read from a header that is never part of the signed content: [5](#0-4) 

`Registry.process` checks only the HMAC over the body, then trusts `request.shop` (and `request.topic`) as authoritative when constructing the metadata handed to the app's handler: [2](#0-1) 

Because a single `api_secret_key` is shared across all shops installed on the app, any body/hmac pair that was legitimately generated for one shop (e.g., a webhook the attacker's own installed shop received, or a webhook the attacker's shop caused to be sent, such as `orders/create` for an order the attacker placed) remains a valid `(raw_body, hmac)` pair regardless of which `shop-domain` header value is sent alongside it. An attacker who controls an app installation on Shop A can capture a genuine `(raw_body, hmac)` pair from their own shop's webhook deliveries, then replay that exact body and HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain: shop-b.myshopify.com`. The HMAC check still passes — it only ever verified the body — yet the host application processes the payload as belonging to Shop B.

This is the same bug class as the RDNT report: a piece of data that is acted upon (`shop`, used for tenant attribution) is not covered by the cryptographic binding (`HMAC` over `raw_body` only), so an unprivileged party who owns one legitimate signed message can redirect its effect onto a different identity/tenant that the binding was supposed to protect.

### Impact Explanation
This maps to the Critical "cross-tenant access" category: a party with access to one tenant's (their own shop's) legitimately-signed webhook traffic can cause the host application to process that data as if it belonged to a different merchant/tenant, since `shop` is the field host apps use to select per-tenant records/handlers. Depending on how the host app uses `WebhookMetadata#shop` (most implementations use it to look up the tenant's session/database row), this can lead to cross-tenant data corruption or disclosure without needing any credentials belonging to the victim shop.

### Likelihood Explanation
Requires only that the attacker controls (or has previously controlled) an app installation on some shop and can trigger/capture at least one webhook delivery for it — a normal unprivileged capability for anyone who can install a public/custom app. No `api_secret_key`, access token, or victim credentials are needed. The attacker only needs the ability to send arbitrary HTTP requests to the app's public webhook endpoint, which is by definition internet-reachable.

### Recommendation
Bind the shop identity into the value that is verified, not just trusted as a bystander header. Options:
- Include the shop domain (and ideally topic) in the signable string used for webhook HMAC verification if the deployment can control it, or
- Cross-check `request.shop` against a shop that the app already has an active, previously-authenticated session/installation record for before processing, rejecting webhooks for domains that were not established through OAuth for that installation context, or
- At minimum, document prominently that `shop`/`topic` header values are unauthenticated relative to the HMAC and must not be trusted for tenant attribution without an independent binding.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) for that shop, capturing the raw POST body and the `x-shopify-hmac-sha256` header value delivered by Shopify.
2. Attacker sends a new POST request to the app's webhook endpoint with the exact same body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and an appropriate `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks the untouched body bytes: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, and the host app processes/stores the attacker's data as belonging to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
