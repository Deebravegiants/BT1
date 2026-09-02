### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing shop-identity spoofing across tenants of the same app - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the `shop` (and `topic`/`webhook_id`/`api_version`) values are read directly from HTTP headers that are excluded from the signed content. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` verbatim to build `WebhookMetadata`, which is handed to the app's handler as the tenant identifier.

### Finding Description
The identity binding that should hold is: `shop header == shop the HMAC signature was generated for`. That binding is never enforced.

- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no relation to the signed bytes: [2](#0-1) 
- `Registry.process` validates HMAC over the body only, then immediately trusts `request.shop` for dispatch: [3](#0-2) 
- The `VerifiableQuery` interface only requires `hmac` and `to_signable_string`, with no hook to bind ancillary header fields into the signature: [4](#0-3) 
- `WebhookMetadata.shop` (built from `request.shop`) is the sole tenant identifier passed to app-supplied handlers: [5](#0-4) 

Because Shopify signs webhooks with the app's single `api_secret_key` — shared across every shop that installs the app, not a per-shop secret — an unprivileged attacker who has installed the app on their own (attacker-controlled) shop legitimately receives genuinely-signed webhook deliveries. Since the HMAC covers only `@raw_body`, the attacker can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only checks the untouched body against the shared secret: [6](#0-5) . The host app then processes data under the spoofed victim shop identity.

### Impact Explanation
This breaks the tenant boundary of the gem's webhook processing: an attacker-controlled shop can cause the app to attribute genuinely-signed webhook payloads/topics (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`, or any topic the attacker can trigger for their own shop) to an arbitrary victim `shop` value. Any host application that keys persistence, deletion, credential revocation, or GDPR redaction logic off `WebhookMetadata#shop` (exactly as the documented usage pattern in `docs/usage/webhooks.md` instructs) can be made to act on the wrong tenant — e.g. deleting or redacting a victim shop's data, or revoking/uninstalling state for a shop the attacker never controls. This is a cross-tenant integrity violation reachable by any unprivileged app-installing user, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any developer using this gem's `Registry.process`/`Request` as documented: no additional binding of header fields to the signature is possible through the public API, so every consumer inherits the gap. The only prerequisite is that the attacker be able to install the app on a shop they control (the normal, unprivileged installation flow) and capture one legitimately delivered webhook to replay with a modified header.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-signed material, or otherwise cryptographically tie the header-derived shop identity to a value verified independently of the mutable HTTP headers (e.g., cross-check against a previously stored session/shop record keyed by webhook subscription id rather than trusting the header alone). At minimum, document that `WebhookMetadata#shop` is unauthenticated with respect to the HMAC and must not be used as a sole tenant-selection key without additional verification (such as confirming an active session/install record for that shop before applying request effects).

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`, triggering a legitimate webhook delivery (e.g. `app/uninstalled`) signed by Shopify with the app's shared `api_secret_key`.
2. Attacker captures the raw POST body and the valid `X-Shopify-Hmac-Sha256` value.
3. Attacker resends the identical body/HMAC to the app's webhook endpoint, replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body`: [7](#0-6) 
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "app/uninstalled", ...)` and performs uninstall/data-deletion logic against the victim tenant.

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L1-16)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
