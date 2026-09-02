## Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted by handlers without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request's authenticity solely by HMAC-verifying the raw request body, then constructs a `WebhookMetadata` object using the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers and passes it to the app's handler. The tenant-identifying `shop` field is never bound by the signature, breaking the equality: `shop authenticated by HMAC == shop attributed to the webhook data`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from HTTP headers, independent of the signed bytes: [2](#0-1) 

`Registry.process` validates only that the HMAC over the raw body matches, using `Utils::HmacValidator.validate`, and then immediately builds `WebhookMetadata` from `request.shop`, `request.topic`, `request.webhook_id`, and hands it to the app-registered handler: [3](#0-2) 

`WebhookMetadata` is the struct the handler interface receives to identify the tenant (`shop`) the payload belongs to: [4](#0-3) 

The HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has installed the app - it is not shop-specific: [5](#0-4) 

Because the signature covers only the body, any party who can obtain one valid `(body, hmac)` pair signed with the app's shared secret — which happens for every legitimate webhook delivered to any shop that installed the app, including an attacker's own store — can replay that exact body/HMAC pair while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header value. `Utils::HmacValidator.validate` will still pass because it only re-computes the signature over `@raw_body`, never over `shop`. `Registry.process` will then invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen shop, causing the application to attribute another tenant's identity to attacker-supplied payload data.

This matches the report's bug class: a field (`shop`) that is acted upon (used to attribute/store data per-tenant) is not covered by the integrity check (HMAC) that is supposed to authenticate the message, i.e. "bytes verified" (raw body) diverges from "bytes/headers parsed and trusted" (shop, topic, webhook_id).

### Impact Explanation
This is a cross-tenant data-integrity issue: an attacker who can trigger any webhook for their own installed store (trivial — e.g., updating their own order/product) can capture the resulting `(body, HMAC)` pair and replay it against the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at an arbitrary victim shop that also has the app installed. Any handler logic keyed by `data.shop` (e.g., updating per-shop records, triggering shop-specific side effects, or writing audit/webhook logs) will act on behalf of the wrong tenant using attacker-controlled body content. This satisfies the "High" bar of cross-tenant access via a scope/identity binding bypass.

### Likelihood Explanation
Exploitation requires: (1) the attacker has (or can obtain) their own app installation, which is the normal case for any public app, and (2) they can send arbitrary HTTP requests to the app's public webhook endpoint, which is inherent to how Shopify delivers webhooks (no network restriction). No secrets, tokens, or privileged access are required beyond having a store where the app is installed — a low bar for a public app. Likelihood is Medium-High.

### Recommendation
Bind the tenant-identifying fields into the signed payload used for HMAC verification, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the signature (e.g., include them in `to_signable_string`, or independently verify `shop` against a value derived from a trusted source such as a previously stored session/shop record rather than trusting the raw header). At minimum, document and/or enforce that consuming applications must not rely on `WebhookMetadata.shop`/`topic`/`webhook_id` as authenticated without additional verification against known/registered shops.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook (e.g., `products/update`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header value `H` (valid because it's signed with the app's single shared `client_secret`).
2. Attacker sends a POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`/`X-Shopify-Webhook-Id` optionally forged too.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` (`to_signable_string`) — validation succeeds because `B` and `H` are unchanged and match. [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop — demonstrating the identity-binding break.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L1-22)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module HmacValidator
      extend T::Sig

      class << self
        extend T::Sig

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
