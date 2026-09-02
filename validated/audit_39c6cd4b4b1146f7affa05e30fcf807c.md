Based on my investigation, this documented behavior confirms the finding: the `shop`, `topic`, `webhook_id`, and `api_version` fields of a webhook are read from HTTP headers but are never included in the HMAC signable string, and this is a known-shape identity binding gap in the gem's own webhook verification implementation.

### Title
Webhook `shop` identity is not bound by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the tenant-identifying `shop` (and `topic`/`webhook_id`/`api_version`) fields are read straight from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body only, then forwards the header-derived `shop` value unchanged to the app's `WebhookHandler` as if it were verified. [1](#0-0) [2](#0-1) 

### Finding Description
`HmacValidator.validate` computes and compares an HMAC-SHA256 over `verifiable_query.to_signable_string` using `Context.api_secret_key`. [3](#0-2) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [4](#0-3) 

But `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled directly from the `x-shopify-*`/`shopify-*` HTTP headers, none of which are part of the signed bytes: [5](#0-4) 

`Registry.process` checks only that the HMAC (over the body) is valid, then constructs `WebhookMetadata` directly from these unauthenticated header values and passes it to the app-supplied handler: [2](#0-1) 

The identity binding broken is: `shop authenticated by HMAC` ≠ `shop delivered to WebhookHandler`. Because a single app's `client_secret` (and thus the HMAC key) is shared across every shop that installs that app, an attacker who legitimately installs the target app on their own (attacker-controlled, free) Shopify development store can trigger any subscribed webhook topic on their own shop, capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair — which is validly signed under the app's single shared secret — and then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop's domain). `HmacValidator.validate` will pass because it only checks the body bytes, and `Registry.process` will hand the forged `shop` straight to the handler, which is documented to key tenant-scoped actions (session lookup, data writes, `app/uninstalled` handling, etc.) off `data.shop`. [6](#0-5) [7](#0-6) 

### Impact Explanation
This is a cross-tenant access vector: an attacker with no relationship to the victim shop can make the app process attacker-controlled webhook bodies under the victim's `shop` identity, since the gem's own `Registry.process`/`HmacValidator` contract offers no protection against header spoofing of `shop`, only body-tamper protection. Any app whose `WebhookHandler` implementation uses `data.shop` to key session lookups, apply state changes, or dispatch `app/uninstalled`/`shop/redact` logic is exposed to spoofed tenant actions using nothing but the attacker's own valid webhook traffic.

### Likelihood Explanation
Likelihood is high for any app that lets outside merchants install it (including via a free development store), since obtaining one valid `(body, hmac)` pair for the attacker's own shop is trivial and the replay requires only a normal unauthenticated POST to the app's public webhook route with a modified header.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise verify the incoming `shop` header against the shop encoded/expected for that specific installation (e.g., compare against a shop known via prior OAuth/session storage) before invoking the handler in `ShopifyAPI::Webhooks::Registry.process`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host app against a known-installed shop list before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker signs up for a free Shopify development store and installs the target app (which uses this gem for webhook processing), granting the app write access only to the attacker's own store.
2. Attacker triggers a subscribed webhook topic (e.g., `orders/create`) on their own store, and captures the outgoing raw body plus the `x-shopify-hmac-sha256` header sent to the app's webhook endpoint — both valid under the app's shared `client_secret`.
3. Attacker sends a new POST request to the same app webhook endpoint with the identical raw body and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` returns `true` (body/HMAC pair is valid). `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and invokes the app's handler, which treats the request as authentically originating from the victim shop. [2](#0-1)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-26)
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
  end
end
```

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
