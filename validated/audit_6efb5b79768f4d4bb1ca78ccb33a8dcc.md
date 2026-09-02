Found it. This is the strongest analog to the reported bug class: an identity field (`shop`) is *used* for tenant identification/dispatch but is **not covered by the HMAC signature** that authenticates the payload.

### Title
Webhook `shop` (tenant) header is not covered by the HMAC signature, allowing cross-tenant data forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC of the body only, then dispatches to the app's handler passing the header-derived `shop` value as trusted tenant identity — exactly the "field acted on but not covered by the HMAC" pattern described in the report's rule set, mirrored in `Registry.process` at `lib/shopify_api/webhooks/registry.rb`.

### Finding Description
`Utils::HmacValidator.validate` verifies `HMAC(body) == header['hmac-sha256']` using `to_signable_string`, which for `Webhooks::Request` is defined as: [1](#0-0) 
This binds only the raw JSON body to the signature. The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` checks only the HMAC of the body, then immediately trusts `request.shop` as the tenant identity when invoking the app's handler: [3](#0-2) 

The equality that should hold is: `shop_bound_by_hmac == shop_used_for_tenant_dispatch`. In this code, the left side does not exist — no `shop` value is included in `to_signable_string` — so the equality is vacuously false. An attacker who can obtain (or replay) *any* single genuine webhook body+HMAC pair signed with the app's `client_secret` (e.g. from their own shop's legitimate webhook, or a leaked/observed webhook payload with a body that is content-agnostic or replayable across tenants) can resubmit that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `Utils::HmacValidator.validate` still succeeds since it only checks the body, and `Registry.process` forwards the attacker-chosen `shop` value to the app's `WebhookHandler#handle` as `WebhookMetadata#shop`, which apps use to scope which merchant's data is affected/looked up.

### Impact Explanation
This breaks tenant isolation for any app relying on this gem's webhook shop identity as an authenticated fact. Since apps commonly use `WebhookMetadata#shop` to select which merchant's stored records to update/delete/redact (e.g. `shop/redact`, `customers/redact`, or app-defined handlers), an attacker controlling only the `shop-domain` header (not requiring `api_secret_key`, tokens, or TLS interception) can cause cross-tenant data corruption or trigger merchant-scoped actions attributed to a shop that never sent the webhook — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitability requires the attacker to possess a body/HMAC pair that Shopify validly signed with the app's secret — normally only Shopify can produce this HMAC without the secret. In practice this is only reachable when the body content is attacker-obtainable/replayable (e.g., a topic whose body is fixed/predictable, or reusing a previously captured legitimate webhook for a different declared shop), which limits likelihood but the root cause — `shop` excluded from the signed payload while used as trusted tenant identity — is a real gap in the gem's own verification path, independent of any specific host-app misuse.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable representation, or otherwise cryptographically bind the header-derived shop domain to the signed body before it is used as tenant identity in `Registry.process`. At minimum, document and enforce that `WebhookMetadata#shop` must be cross-checked by the host app against a shop known to be already installed/authorized, and consider validating the `shop-domain` header format via `Utils::ShopValidator` plus binding it into the signature computation.

### Proof of Concept
1. Attacker's own shop (or an observed webhook) produces a legitimate `(raw_body, hmac)` pair signed by the app's `client_secret_key`, e.g. via `OpenSSL::HMAC.digest(sha256, secret, raw_body)` as shown in test setups: [4](#0-3) 
2. Attacker resends the same `raw_body` and `shopify-hmac-sha256` value to the app's webhook endpoint, but sets `shopify-shop-domain` to a victim shop's domain.
3. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the HMAC — the shop header is never part of the signed content: `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with the forged victim shop domain: `lib/shopify_api/webhooks/registry.rb:198-199`, causing the app to act on/attribute data to the wrong tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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

**File:** test/webhooks/registry_test.rb (L284-298)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
```
