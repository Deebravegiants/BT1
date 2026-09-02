Confirmed. In `Registry.process` at `lib/shopify_api/webhooks/registry.rb:188-200`, the only authentication check is `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` — and `Webhooks::Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38` returns only `@raw_body`. The `shop` field returned by `request.shop` (`lib/shopify_api/webhooks/request.rb:20-23`) comes from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is **not** part of the HMAC-signed material at all. That `shop` value is then passed straight into `WebhookMetadata` and handed to the app's `handler.handle` as the tenant identifier, with no cross-check against the body or any other signed field.

### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, while `ShopifyAPI::Webhooks::Request#shop` is read from an unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC over the body only, then trusts the header-derived `shop` as the tenant for the webhook, breaking the intended binding `hmac == HMAC(body, secret) AND shop is authenticated`.

### Finding Description
`Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field. For `Webhooks::Request`, `to_signable_string` returns `@raw_body` exclusively (`lib/shopify_api/webhooks/request.rb:35-38`); the `shop`, `topic`, `webhook_id`, and `api_version` values are pulled straight from HTTP headers (`shopify_header`, lines 20-33) that are never included in the signed string. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC, then immediately builds `WebhookMetadata` using `request.shop` — the header value — as the authoritative tenant identifier for the app's handler, with no verification that this header matches whatever shop the body content actually pertains to.

This creates an identity-binding gap analogous to the referenced M-6 report: the mechanism meant to authenticate the request (`HmacValidator.validate`) covers only the body, but the field the application logic actually keys its trust decision on (`shop`) is outside that coverage.

### Impact Explanation
Because the shop-domain header is unauthenticated, an app that dispatches any per-shop behavior in its webhook handler based on `data.shop` (multi-tenant data storage/routing, access-control decisions, session lookups, etc.) can be made to process a validly-HMAC'd body under an attacker-chosen shop identity, as long as the attacker can supply *some* raw body + valid HMAC pair for the app's secret and freely set the shop-domain header on the request it forwards to the app's webhook endpoint. Since header values are not part of what's cryptographically bound, this can lead to cross-tenant confusion in the receiving application when it trusts `WebhookMetadata#shop`.

### Likelihood Explanation
This requires an attacker to have access to at least one legitimately-computed `(raw_body, hmac)` pair for the target app (e.g., replaying/relaying a real webhook delivery, or triggering a public/predictable-body webhook aimed at their own shop) and the ability to control the HTTP headers of the request reaching the app's webhook endpoint (i.e., they are relaying/forwarding rather than Shopify delivering directly). It does not require possession of `api_secret_key` itself, only a valid signed body obtained through legitimate use.

### Recommendation
Include the shop-domain (and ideally topic/webhook_id) in the HMAC-signed material, or otherwise independently verify that the `shopify-shop-domain` header matches an expected/authenticated value (e.g., cross-check against a shop registered for that webhook subscription) before trusting `request.shop` in `WebhookMetadata`.

### Proof of Concept
```ruby
# Attacker has legitimately received one webhook for their own shop "attacker.myshopify.com"
# with body B and a valid hmac H = HMAC_SHA256(secret, B) computed by Shopify.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(H), # valid, unmodified
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # swapped, unauthenticated
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) passes because it only checks HMAC(B, secret) == H
# handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
``` [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
