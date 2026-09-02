### Title
Webhook `shop`/`topic` identity is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, and `webhook_id` values that the SDK hands to the registered handler are taken from unauthenticated HTTP headers that are never included in the signable string.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it to the `hmac` header value: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof of authenticity for the whole request, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by the signature — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`request.shop` and `request.topic` are read straight from the `shopify-shop-domain` and `shopify-topic` HTTP headers with no cryptographic binding to the body: [4](#0-3) 

The broken identity binding, stated as an equality that the gem fails to enforce:
`HMAC(secret, raw_body) valid` should imply `shop header == shop that HMAC was computed for`, but the gem only proves `HMAC(secret, raw_body) valid`, not `shop == authenticated_shop`.

Because the app's own shop legitimately receives webhooks (Shopify computes a real, correctly-signed `hmac` over the JSON body it sends for that shop's events), an unprivileged party who controls a shop installed on the same app can capture a genuinely-signed `(raw_body, hmac)` pair from their own store's webhook delivery, then replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header with a victim shop's domain (or a different registered topic). `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen victim domain — an identity that was never authenticated.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to provide to handler code: any host application that keys business logic off `WebhookMetadata#shop` (e.g., `shop/redact`, `customers/redact`, `app/uninstalled` handling, data deletion, or session/state invalidation per shop) can be made to act on a shop it was not actually notified about, from a request that only required control of one's own (attacker's) shop and knowledge of when a webhook fires. This is a cross-tenant integrity issue at the SDK boundary the app is instructed to trust (`Registry.process` guarantees "HMAC valid" but that guarantee does not extend to `shop`/`topic`).

### Likelihood Explanation
Reaching this requires: (1) the attacker operates a store that has the target app installed (unprivileged relative to other merchants — no access token, secret, or victim credentials needed), (2) the attacker can intercept/capture one webhook delivery for their own shop (webhooks are delivered over HTTP(S) to the app's public endpoint; a shop owner controls their own storefront actions that trigger webhooks and can be a passive observer of their own webhook traffic if they run the app's endpoint or a proxy in front of it), and (3) the app's webhook endpoint is reachable to replay requests with attacker-controlled headers. No leaked `api_secret_key`, access token, or TLS interception of someone else's traffic is required.

### Recommendation
Bind the authenticated identity to the signature: either (a) include `shop`, `topic`, and `webhook_id` in the signable string alongside the body, or (b) after validating the body HMAC, independently verify `request.shop` against the shop the handler expects for that delivery context (e.g., require callers to supply the expected shop and compare it, rather than trusting the header value implicitly). At minimum, document loudly in `Webhooks::Request`/`Registry` that `shop`/`topic` are unauthenticated metadata and must not be used for authorization decisions without additional verification.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` has the app installed; Shopify delivers a legitimately signed webhook with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: app/uninstalled`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`.
2. Attacker replays the identical body and `hmac` header to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) returns `true` because only the body bytes are checked.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the app's `app/uninstalled` (or other) handler with `shop: "victim.myshopify.com"`, causing the app to act as if the victim shop sent that event. [3](#0-2) [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-38)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
