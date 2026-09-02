### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` (and `topic`/`api_version`/`webhook_id`) values come from unauthenticated HTTP headers that are never included in the signed payload. `Registry.process` validates the HMAC and then forwards `request.shop` straight into `WebhookMetadata`, which app code uses to attribute the event to a merchant/tenant.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, bytes_that_determine_the_action)`. Here the "action" includes attributing the payload to a specific shop, but the signed bytes are only the body: [1](#0-0) 

`to_signable_string` returns `@raw_body` alone — the `shop-domain` header is excluded from the signable string, yet `shop` is read straight from that same untrusted header: [2](#0-1) 

`HmacValidator.validate` only checks `to_signable_string` against the secret, so it can never detect tampering with `shop`, `topic`, `api_version`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates HMAC, then hands `request.shop` (and other unsigned headers) directly to the handler as authenticated-looking data: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` const with no further verification, so any host application built on this gem's documented API receives an attacker-controllable `shop` value alongside a body that legitimately passed HMAC verification: [5](#0-4) 

Because the HMAC only binds `secret ⟺ body`, and not `secret ⟺ (body, shop)`, an unprivileged internet user who legitimately receives real Shopify webhooks for their own store (any merchant/app installer can do this) can capture a valid `(raw_body, hmac)` pair and replay it directly to the target application's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a victim shop. `HmacValidator.validate` still returns `true` because the signature check is body-only, and `Registry.process` will call the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain, even though the body/topic content actually belongs to the attacker's own shop.

### Impact Explanation
This breaks the tenant-identity binding the gem is documented to provide (`request.shop` is meant to be the authenticated originating shop of the signed payload). An application that uses `data.shop` from `WebhookMetadata` to select which merchant record/session/data to update, per the gem's own documented webhook contract, can be made to attribute attacker-supplied webhook content to an arbitrary other tenant, i.e., cross-tenant access/confusion, without any credentials, valid session, or knowledge of the app's `api_secret_key`.

### Likelihood Explanation
Any user who can trigger a legitimate webhook for their own shop (installing the app on a free/dev store is enough) obtains a valid `(body, hmac)` pair signed with the app's real secret. Replaying that pair to the app's public webhook endpoint with a modified `shop-domain` header requires only a normal HTTP client — no interception, no leaked secrets, and no privileged access, since `shop` is never covered by the signature the gem itself computes.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in `to_signable_string` of `ShopifyAPI::Webhooks::Request`, or otherwise cryptographically bind the shop identity to the signed payload before exposing it via `WebhookMetadata`, so that `HmacValidator.validate` fails whenever any of these identity-bearing fields are altered from what Shopify actually signed.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) to receive a real request with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - raw body `B`
2. Send a new HTTP request to the app's webhook endpoint with the identical raw body `B` and identical `x-shopify-hmac-sha256`, but replace the header with `x-shopify-shop-domain: victim.myshopify.com`.
3. Server code calls `ShopifyAPI::Webhooks::Registry.process(request)`:
   - `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) only hashes `@raw_body`, unaffected by the header change.
   - `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` (`lib/shopify_api/webhooks/registry.rb:198-199`) is invoked with `shop == "victim.myshopify.com"`, even though the payload originated from and was signed for `attacker.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L4-12)
```ruby
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
