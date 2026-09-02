### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted but not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers and hands them to the host app's handler as verified metadata. The identity-binding equality the report's bug class targets is: `bytes verified == bytes acted on`. Here that equality is broken because the bytes verified by `HmacValidator.validate` (the JSON body only) are not the same bytes the handler treats as authoritative for tenant identity (the `shop-domain` header).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`hmac` is likewise read straight from a header: [2](#0-1) 

but `shop`, `topic`, `webhook_id`, and `api_version` are read from separate headers that are never mixed into `to_signable_string`: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body only) and compares it with `OpenSSL.secure_compare`: [4](#0-3) 

`Registry.process` uses exactly this validation, then constructs `WebhookMetadata` directly from the unauthenticated header-derived fields, including `shop`: [5](#0-4) 

`WebhookMetadata.shop` is a plain `String` const with no further verification, and is the value host applications are expected to use as the tenant identifier for the webhook: [6](#0-5) 

Because `api_secret_key` is shared across every shop that has the app installed, any unprivileged internet user can install a public app on their own store, receive a genuine webhook (valid body + valid HMAC for their own shop), and then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`/`X-Shopify-Api-Version`) header with an arbitrary victim shop domain. Since these header values are never part of the signed payload, `HmacValidator.validate` still returns `true`, and `Registry.process` forwards `shop: <attacker-chosen value>` to the app's handler as though it were an authenticated fact from Shopify.

### Impact Explanation
This breaks the cross-tenant isolation the gem is supposed to guarantee for webhook processing: the `shop` field consumed by the host application's `WebhookHandler#handle` implementation is not bound to the HMAC that "proves" the message came from Shopify. Any app that keys persistence, cache invalidation, feature entitlement, or authorization decisions off `WebhookMetadata#shop` can be made to process a payload as belonging to an arbitrary victim shop, i.e., cross-tenant data confusion/injection driven entirely by an attacker who has legitimately installed the app on their own (attacker-controlled) shop. This matches the Critical bucket in scope ("cross-tenant access").

### Likelihood Explanation
Likelihood is high: exploitation requires no leaked secrets, no privileged account beyond installing a (typically free) public app on the attacker's own store, and no interaction with TLS or the host's infrastructure — only the ability to trigger a real webhook (e.g., `orders/create`) on the attacker's own shop and replay the captured body+HMAC with a modified `shop-domain` header value to the same publicly reachable webhook endpoint.

### Recommendation
Include the `shop`, `topic`, `webhook_id`, and `api_version` values in the signable payload used for HMAC verification (or otherwise cryptographically bind them, e.g., HMAC over a canonical string that concatenates the header values with the body) so that any tampering with those headers invalidates the signature. At minimum, document and enforce that `shop` must be cross-checked by the host application against a shop this specific app instance actually has an active session/webhook subscription for, rather than trusting the header value as-is.

### Proof of Concept
1. Install the target public app on an attacker-controlled store `attacker.myshopify.com` (any internet user can do this for a public app).
2. Trigger a webhook event (e.g., create an order) on `attacker.myshopify.com`; capture the resulting POST request, including the JSON body and the `X-Shopify-Hmac-Sha256` header — this HMAC is valid because `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` only checks the body against `Context.api_secret_key`, which is the same secret for every shop.
3. Replay the identical body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and adjust `X-Shopify-Topic`/`X-Shopify-Webhook-Id` if desired).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` which returns `true` (only body was checked), and the handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
