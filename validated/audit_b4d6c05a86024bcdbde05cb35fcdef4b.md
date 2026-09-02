### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing via webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which merchant the payload belongs to. Because the header is not part of the signed data, any attacker who possesses a single validly-signed webhook payload (e.g. from their own store where they legitimately received a webhook for the app) can replay that exact body+HMAC pair while substituting an arbitrary `shop-domain` header, and the gem will process it as if it originated from the spoofed shop.

### Finding Description
The HMAC validation binding is: `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` where `to_signable_string` returns `@raw_body` only for webhook requests: [1](#0-0) [2](#0-1) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the HMAC: [3](#0-2) 

`Registry.process` validates only the HMAC (over body bytes) and then forwards the header-derived `shop` value straight to the app-supplied handler as trusted metadata: [4](#0-3) 

The generic `HmacValidator.validate` / `validate_signature` logic reused here compares `verifiable_query.hmac` against a signature computed over `verifiable_query.to_signable_string`: [5](#0-4) 

The equality that the gem should be enforcing is: `shop_header_trusted_by_handler == shop_that_the_HMAC_actually_authenticates`. Instead, the HMAC authenticates only `raw_body`, and `shop` is taken from an independent, unauthenticated header. Any party that can obtain one legitimately-signed webhook (trivially available to any developer/merchant who installs the app on their own store and receives a real webhook from Shopify) can resend that exact `raw_body`/`hmac` pair to the app's webhook endpoint while changing the `shop-domain` header to a victim shop's domain. `Registry.process` will pass the HMAC check (body bytes are unchanged) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

This mirrors the reported bug class ("a value is used/trusted without being validated against the bound reference"): here the field acted upon (`shop`) is not covered by the same binding (`HMAC`) that authenticates the request as genuinely from Shopify.

### Impact Explanation
Any host application that uses `data.shop` from `WebhookMetadata` to key persistence, trigger per-shop side effects, or attribute webhook data (as the gem's own documentation instructs: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) is exposed to cross-tenant data confusion: an attacker can inject arbitrary Shopify-shaped payloads (constrained to bodies they can obtain a valid signature for) under a victim shop's identity. Depending on how the host app uses this metadata (e.g., writing to victim shop's local records, triggering webhook-driven business logic attributed to the wrong tenant), this can constitute cross-tenant data corruption/confusion without ever needing the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
Low-to-moderate. The attacker needs at least one genuinely HMAC-signed webhook body (easily obtained by installing the target app on their own store, a normal unprivileged action), and a way to invoke the app's public webhook endpoint with custom headers (webhook endpoints are, by design, public HTTP endpoints accepting POSTs from "Shopify"). No secret, token, or victim credential is required.

### Recommendation
Bind the shop identity to the same authenticated channel as the body, or otherwise defend against header spoofing:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values inside the signable string that the HMAC covers, mirroring what `AuthQuery#to_signable_string` does for OAuth callbacks.
- Alternatively/additionally, require host applications to cross-check `data.shop` against a shop for which a webhook was actually registered/subscribed (e.g., validate against known sessions) before trusting it, and document this requirement prominently since the current docs imply `data.shop` can be trusted directly.

```diff
 sig { override.returns(String) }
 def to_signable_string
-  @raw_body
+  "#{shop}\n#{topic}\n#{webhook_id}\n#{@raw_body}"
 end
```

### Proof of Concept
1. Install the target app on an attacker-controlled store `attacker.myshopify.com` and trigger a subscribed webhook topic (e.g. `orders/create`) so Shopify sends a legitimately-signed webhook to the app's endpoint. Capture the raw POST body and the `x-shopify-hmac-sha256` header value — these are valid because Shopify itself signed them with the app's `api_secret_key`.
2. Replay the exact same body and HMAC header to the app's public webhook endpoint, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` computes the HMAC over `raw_body` only (`lib/shopify_api/webhooks/request.rb#to_signable_string`), which matches the replayed signature, so validation succeeds.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body, even though this data never came from Shopify on behalf of the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
