Confirmed: `Registry.process` passes `request.shop` (from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header) straight into `WebhookMetadata`, while the HMAC only signs `@raw_body`.### Title
Webhook shop-domain identity is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw request body only, while the shop-tenant identity (`shop-domain` header) is read separately and never bound by the HMAC. `Registry.process` validates the HMAC, then blindly forwards the unauthenticated `shop` value to the app's `WebhookHandler`. This breaks the identity binding `HMAC-verified content == HMAC-verified shop`, analogous to the report's fee mechanism acting on a broader liquidity/state set than what is actually attributed/verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from an ordinary HTTP header that is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` only ever verifies `to_signable_string` (i.e. the body) against the computed HMAC — it never touches `shop`, `topic`, `webhook_id`, or `api_version`: [3](#0-2) 

`Registry.process` checks only that HMAC, then constructs `WebhookMetadata` using the unauthenticated `request.shop` field and hands it to the app's handler as the trusted tenant identifier: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` const with no further verification, and this is the only field host apps have to determine "which merchant does this webhook belong to": [5](#0-4) 

**The broken equality:** the gem implicitly claims `hmac_verified(raw_body) ⇒ shop == authenticated_tenant`, but the actual guarantee is only `hmac_verified(raw_body)`; `shop` is taken from an ordinary, unsigned header. Because the same `api_secret_key` is shared across every shop that installs a given app (it is a per-app secret, not per-shop), any shop that has installed the app can trigger a webhook on its own store to obtain a body + valid HMAC pair signed with that shared secret, then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header value for a different, victim shop's domain. `HmacValidator.validate` will still pass (it only checks the body), and `Registry.process` will dispatch the payload to the handler tagged with the attacker-chosen `shop`.

### Impact Explanation
This yields cross-tenant data injection/confusion: an unprivileged but existing app-installer (any merchant who installed the multi-tenant app) can cause the host application to process attacker-controlled webhook data under a victim shop's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up the victim's session/access token, updating the victim's local records, triggering mandatory-webhook data flows), this can lead to cross-tenant data corruption or triggering privileged actions against another merchant's records — a cross-tenant access issue within the impact categories in scope.

### Likelihood Explanation
Medium-to-High for any app built on this gem: the attacker only needs to be a legitimate (even free/trial) installer of the same app, generate a webhook on their own store (e.g. by placing/cancelling an order, or any topic they've subscribed to), capture the raw POST body and its `X-Shopify-Hmac-Sha256` header, and resend it to the app's public webhook URL with a forged shop-domain header. No secret material, TLS interception, or social engineering is required — only the gem's own header-parsing/HMAC-check code path (`Request#initialize`, `HmacValidator.validate`, `Registry.process`) is exercised.

### Recommendation
Bind the shop identity into the HMAC-verified surface, or otherwise independently authenticate it before trusting it as a tenant key: e.g., include `shop`, `topic`, `webhook-id`, and `api-version` header values in the signable string used for the HMAC computation, or require that `request.shop` matches a shop known to have an active session/registration for that specific `webhook_id`/topic before dispatching to the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional server-side reconciliation (e.g. checking against the shop that the app registered the given `webhook_id` for).

### Proof of Concept
```ruby
# Attacker owns shop "attacker.myshopify.com", installed on the same app.
# Step 1: Attacker triggers a webhook (e.g. orders/create) on their own store,
# capturing the raw body their app receives and the "x-shopify-hmac-sha256" header
# Shopify sent — this HMAC is valid because it's signed with the app's shared
# api_secret_key, not something shop-specific.

raw_body     = '{"id":1,"note":"forged payload"}'
valid_hmac   = "<HMAC captured from Shopify's own POST to attacker's endpoint>"

# Step 2: Attacker replays the exact same body+HMAC to the target app's public
# webhook endpoint, but swaps only the shop-domain header:
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => valid_hmac,       # unchanged, still validates raw_body
  "x-shopify-shop-domain"  => "victim.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes because HmacValidator only checks raw_body against the shared secret:
ShopifyAPI::Webhooks::Registry.process(request)
# => Handler#handle is invoked with WebhookMetadata(shop: "victim.myshopify.com", ...)
#    even though the payload never originated from Shopify on victim's behalf.
``` [4](#0-3) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
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
