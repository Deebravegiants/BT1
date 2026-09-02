### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/verifies the HMAC exclusively over that raw body. The `shop` (and `topic`, `api_version`, `webhook_id`) values that the library hands to the app's handler via `WebhookMetadata` come straight from HTTP headers (`x-shopify-shop-domain`, etc.) which are never included in the HMAC-signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler: [1](#0-0) 

`HmacValidator.validate` verifies the signature against `verifiable_query.to_signable_string`: [2](#0-1) 

For webhooks, `to_signable_string` is defined to return *only* the raw body, not the shop-domain, topic, or webhook-id headers: [3](#0-2) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all parsed straight from the (unauthenticated) HTTP headers: [4](#0-3) 

These header-derived values are then passed directly into `WebhookMetadata`, the object the host application's handler uses to determine which tenant ("shop") the payload belongs to: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac == HMAC(secret, body || shop || topic || webhook_id)`, i.e. the tenant identifier acted upon (`shop`) should be cryptographically bound to the same bytes that are verified. Instead, only `body` is covered: `hmac == HMAC(secret, body)`, while `shop` is a free-form header value that is never authenticated.

Because the signature is a function of the body alone, any two webhook deliveries (for the same app/`client_secret`) that happen to carry byte-identical bodies will produce byte-identical, valid HMAC values — regardless of which shop the header claims to be from. An attacker who controls a shop that has installed the app (an "unprivileged internet user" with respect to other tenants of the same app) can:
1. Trigger/capture a legitimate webhook delivery to the app for their own shop, with a body that is empty or otherwise generic across shops (e.g. `shop/redact`, `app/uninstalled`, or any topic whose payload doesn't embed shop-specific fields the app checks).
2. Replay that exact `raw_body` + valid `hmac`, but substitute the `x-shopify-shop-domain` header with the victim shop's domain.
3. `HmacValidator.validate` still succeeds since it never inspects the header, and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the victim's domain.

### Impact Explanation
This breaks the cross-tenant boundary the gem is supposed to enforce for webhook delivery. A host application that trusts `WebhookMetadata#shop` (as documented/intended usage, see `docs/usage/webhooks.md`) to select which tenant's data to update, delete, or redact could be made to act on the wrong tenant's records using attacker-controlled but validly-signed payloads. Depending on the topic (e.g. `customers/redact`, `shop/redact`, `app/uninstalled`), this can cause cross-tenant data manipulation/deletion — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitability requires the attacker to operate a shop that has the vulnerable app installed (readily achievable for any public app) and to find or produce a webhook topic whose body content is generic/empty so that a captured signature is reusable across shops. Many mandatory/compliance webhook topics (e.g. `shop/redact`) have minimal or predictable bodies, making this practical rather than theoretical.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values to the authenticated bytes before trusting them, e.g. by including the `x-shopify-shop-domain` header in the signable string used for HMAC verification (matching Shopify's actual webhook validation model, which additionally requires operators to cross-check the shop domain against their own registered installations), or by requiring the caller to independently verify that `request.shop` corresponds to a shop with an active installation before dispatching to a handler. At minimum, `Registry.process` should not treat `request.shop` as trustworthy without an out-of-band tenant check.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`. Attacker triggers a webhook with a generic/empty body (e.g. `shop/redact` compliance webhook), capturing:
   - `raw_body = "{}"`
   - `x-shopify-hmac-sha256 = Base64(HMAC-SHA256(client_secret, "{}"))`
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/request.rb:21`).
4. `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only and it matches, since the shop header isn't part of the signed data (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` dispatches to the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to act on the victim tenant using an attacker-forged (but validly-HMAC'd) request.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
