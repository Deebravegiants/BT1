### Title
Webhook `shop` domain used as tenant identifier is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body` [1](#0-0) , while `shop` is read directly from the `X-Shopify-Shop-Domain` HTTP header, entirely outside the HMAC's signed content [2](#0-1) . `Registry.process` validates the HMAC over the body only, then forwards `request.shop` verbatim into `WebhookMetadata` as the tenant identifier passed to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `hmac_signed_bytes == bytes_that_determine_tenant`. Here it does not: `HmacValidator.validate(request)` verifies `HMAC(secret, raw_body) == header["hmac-sha256"]` [4](#0-3) , but the tenant-identifying `shop` field comes from a separate, unsigned header [2](#0-1) . Any request whose body/HMAC pair is valid for the app's secret (e.g., a genuine webhook the attacker legitimately received for their own store) can have its `X-Shopify-Shop-Domain` header rewritten to any other shop domain and will still pass `Utils::HmacValidator.validate(request)`, because the header is never part of the signed content [5](#0-4) . `WebhookMetadata.shop` then carries this attacker-controlled value straight to the host app's handler [6](#0-5) , so the app cannot distinguish "the body I signed" from "the shop I'm being told this belongs to."

### Impact Explanation
Any app that keys per-tenant state (e.g., app uninstall processing, data-erasure/GDPR topics, or store-specific data updates) off `WebhookMetadata#shop` can be made to apply a webhook payload legitimately signed for the attacker's own store to a victim shop merely by relabeling the header. This is a cross-tenant identity confusion at the boundary this gem exposes to the host application, matching the audit's root cause pattern (a value used to bind two authenticated views of state that is not itself covered by the verification check).

### Likelihood Explanation
An attacker needs only their own valid app installation (any merchant can install/uninstall a public app) to obtain a genuinely HMAC-signed webhook body/signature pair, then replay it against the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header — no access to `api_secret_key` or a victim's access token is required.

### Recommendation
Bind `shop` (and `topic`/`webhook_id` if used for authorization decisions) into the HMAC-signed content, or require the caller to independently verify the shop domain (e.g., against a known/installed-shop allow-list) before trusting `WebhookMetadata#shop`, rather than trusting the raw header once only the body's HMAC has been checked.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook: raw body `B`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
2. Attacker resends the exact same body `B` and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` against the header — it passes because `B` and the HMAC are unchanged [5](#0-4) [4](#0-3) .
4. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop == "victim.myshopify.com"` [7](#0-6) , and the host app's handler processes the attacker's payload as if it originated from the victim's store.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
