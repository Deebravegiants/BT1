This confirms the analog. The `shop` field delivered to `WebhookMetadata` (and thus to the handler) is read from the `shop-domain` HTTP header, while the HMAC signature only covers the raw request body.

### Title
Webhook `shop` identity is trusted from an unauthenticated header not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant identifier (`shop`) from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body, never the `shop` header. This breaks the binding `hmac_signed_bytes == bytes_the_app_trusts_for_tenant_identity`, allowing the `shop` value dispatched to the merchant's webhook handler to be forged independently of the cryptographic signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` reads a plain, unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC over `request` (i.e., over `raw_body` only via `VerifiableQuery#to_signable_string`), and then immediately hands `request.shop` to the handler as trusted tenant identity without any additional binding check: [3](#0-2) 

`VerifiableQuery` only requires `hmac` and `to_signable_string`, and `HmacValidator.validate` simply recomputes the HMAC of `to_signable_string` and compares it to the supplied `hmac`: [4](#0-3) [5](#0-4) 

Since `shop-domain` is not part of the signed bytes, `WebhookMetadata.shop` — the field the app's handler uses to know *which merchant/tenant* the payload belongs to — is not bound to the HMAC at all: [6](#0-5) 

The binding that should hold is:
`HMAC-verified bytes == bytes that determine tenant identity used by the handler`

But in practice:
`HMAC-verified bytes (raw_body only) != bytes used for tenant identity (shop-domain header)`

**Attack sequence (unprivileged internet user with a legitimate, self-controlled Shopify store):**
1. Attacker installs the vulnerable app on their own (attacker-owned) shop `attacker.myshopify.com` — a fully unprivileged, self-service action.
2. Attacker triggers any webhook topic the app subscribes to for their own shop (e.g. by creating an order), causing Shopify to deliver a webhook to the app's HTTP endpoint with a valid HMAC computed over the JSON body using the app's real `client_secret`.
3. Attacker captures this `(raw_body, hmac)` pair — both are visible to them since it's their own webhook delivery.
4. Attacker replays the exact same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but substitutes the `shop-domain` header (or `x-shopify-shop-domain`) with a victim shop's domain, e.g. `victim.myshopify.com`.
5. `HmacValidator.validate` still succeeds because it only recomputes the HMAC over `raw_body`, which is unchanged.
6. `Registry.process` dispatches to the handler with `WebhookMetadata.shop == "victim.myshopify.com"`, even though the actual signed content originated from the attacker's own store.

### Impact Explanation
This is a cross-tenant confusion: an app's webhook handler typically uses `data.shop` to decide which tenant's records to create/update/delete (e.g., "update order X for shop Y", "redact customer data for shop Y"). Because the `shop` value is fully attacker-controlled and unauthenticated relative to the HMAC, an attacker who legitimately installs the app on their own store can inject data attributed to, or trigger side effects against, an arbitrary victim shop record inside the host application — a cross-tenant access impact.

### Likelihood Explanation
Any unprivileged actor can install the app (or already has installed it) on a shop they control and can trigger real webhook deliveries at will, giving them a valid `(body, hmac)` pair. Forging the `shop-domain` header only requires replaying an HTTP request with a different header value — no cryptographic secret, access token, or privileged account is needed. The only prerequisite is knowledge of the app's webhook endpoint URL, which is typically not secret.

### Recommendation
Bind the trusted `shop` identity to the signed payload instead of an independent header:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) values inside the signable string used for HMAC verification, or
- Cross-check `request.shop` against the shop associated with the specific webhook subscription/registration being processed (e.g., correlate `webhook_id` to a known registration and its expected shop) before dispatching to the handler, or
- At minimum, document/require that host applications independently verify `shop` against their own session store rather than trusting the header value emitted by this gem.

### Proof of Concept
```ruby
# Step 1: Attacker triggers a real webhook to their own shop and captures body + hmac
raw_body = '{"id":123,"note":"hello"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
# (This is a legitimate delivery Shopify sent for attacker.myshopify.com)

# Step 2: Attacker replays it, spoofing the shop-domain header
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "shopify-shop-domain" => "victim.myshopify.com",   # <-- forged, not covered by HMAC
  "shopify-webhook-id" => "any-id",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HmacValidator.validate(request) == true, because it only checks raw_body against valid_hmac
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", ...))
# The host app now believes this payload legitimately belongs to victim.myshopify.com.
```

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L1-17)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
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
