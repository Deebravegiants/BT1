### Title
Webhook shop-domain identity is unauthenticated (not covered by HMAC), enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request **body**, but the `shop` identity that host applications rely on to attribute the webhook to a tenant is taken from an HTTP header that is never included in the signed bytes. This breaks the equality that should hold: `shop authenticated by HMAC == shop used as the tenant identity delivered to the handler`. In reality, `shop_covered_by_hmac == ∅` while `shop_delivered_to_handler == header["shop-domain"]`, an attacker-controlled value.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic relationship to the HMAC: [2](#0-1) 

`HmacValidator.validate` only ever calls `to_signable_string` (i.e., the body) against the HMAC secret — it never touches headers: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authentication, then forwards the unauthenticated `request.shop` straight to the app's handler as the tenant identity: [4](#0-3) 

Because the app's `client_secret`/`api_secret_key` is shared across **all** shops that have the app installed (it is not per-shop), any unprivileged internet user can install the app on their own store (or dev store), capture a legitimate, correctly-HMAC-signed webhook body from their own shop, and replay that exact `raw_body` + `hmac` pair directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass because the signature only covers `@raw_body`, which the attacker copied verbatim and did not tamper with. The gem then hands the handler a `WebhookMetadata` whose `shop` field is the victim's domain, even though the body content and signature were never associated with that shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem asserts to the host application that a webhook payload is attributable to shop X (`request.shop`), while the only cryptographic guarantee it actually provides is "these bytes were signed with the app's secret" — with no guarantee about which shop produced them. Any host application that uses `WebhookMetadata#shop` (as documented and exemplified in `docs/usage/webhooks.md`) to select which tenant's data/session to update will process the attacker's replayed payload under the victim's shop identity. Depending on the webhook topic (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`, order/customer topics), this can result in cross-tenant data corruption, spurious redaction/uninstall processing against a shop that never sent the event, or state confusion between tenants — a cross-tenant access impact.

### Likelihood Explanation
High for any app that (a) allows self-serve/dev-store installs (typical for any published or partner-development app) and (b) uses the `shop` field from `WebhookMetadata` for tenant routing, which is the documented, expected usage pattern of this gem. No secrets, TLS interception, or privileged accounts are required — only the ability to install the app once as an ordinary merchant and to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material used by `Utils::HmacValidator`, or independently verify that `request.shop` corresponds to a shop for which the app holds an active session/installation before trusting it as tenant identity in `Registry.process`. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must be cross-checked by the host application against known installed shops before being used as a trust boundary.

### Proof of Concept
1. Attacker installs the target app on their own (attacker-controlled) Shopify dev store `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook to the app, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: customers/redact
   x-shopify-hmac-sha256: <valid HMAC of body, signed with app's shared api_secret_key>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"customer": {...}, "orders_to_redact": [...]}
   ```
3. Attacker captures the raw body and the `x-shopify-hmac-sha256` value unmodified.
4. Attacker sends a forged request directly to the app's public webhook endpoint:
   ```
   POST /webhooks
   x-shopify-topic: customers/redact
   x-shopify-hmac-sha256: <same captured HMAC>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: <same captured raw body, byte-for-byte>
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `OpenSSL::HMAC.hexdigest` over `request.to_signable_string` (the untouched raw body) — this matches, so validation succeeds: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's original payload>, ...)`, and the host app processes/attributes the event as if it originated from the victim shop.

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
