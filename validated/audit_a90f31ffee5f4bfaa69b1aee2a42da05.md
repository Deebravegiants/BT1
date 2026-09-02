### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC validation performed in `ShopifyAPI::Webhooks::Registry.process` cryptographically authenticates the **body bytes** only. The `shop-domain`, `topic`, `webhook-id` and `api-version` values, which are taken verbatim from unauthenticated HTTP headers, are never bound to that signature, yet they are trusted and handed to the app's webhook handler as the tenant identity for the event.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns `@raw_body` only — none of the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers are included in the signed material. `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are simple header reads with no cross-check against the body: [2](#0-1) 

`Registry.process` validates only this HMAC (i.e., only the body) and then constructs `WebhookMetadata` directly from the unauthenticated header-derived `request.shop`: [3](#0-2) 

`WebhookMetadata.shop` is the sole tenant identifier passed to the host application's handler: [4](#0-3) 

Because the `api_secret_key` is shared across all shops installing the same app (it is not shop-specific), an unprivileged internet user who controls one shop that has the app installed (or who otherwise obtains one legitimate `(raw_body, hmac)` pair produced with the app's secret — e.g. by observing their own shop's webhook deliveries) can compute a valid HMAC for an arbitrary body of their choosing, since the signature depends only on `raw_body` and the shared secret. They can then freely set the `shopify-shop-domain` header to any victim shop's domain when POSTing to the app's public webhook endpoint. `Utils::HmacValidator.validate` will succeed because it only re-derives the signature from `@raw_body`: [5](#0-4) 

The equality that should hold is: `shop authenticated by the signature == shop delivered to the handler as the tenant`. In this gem, the shop bound to the HMAC is "none" (empty set) while the shop delivered to the handler is an attacker-chosen header value — the two are never required to be equal.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): an attacker can make the app believe an arbitrary, attacker-crafted payload — with a topic of their choosing (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`) — originated from any victim shop domain, as long as they can produce one valid `(body, hmac)` pair with the shared app secret. Downstream host applications (per this gem's documented handler contract in `docs/usage/webhooks.md`) are expected to trust `data.shop` to determine which tenant's records to create/update/delete or which tenant's session to look up for follow-up API calls, since the gem provides no other authenticated shop signal. This can lead to injecting fabricated data into another merchant's records, triggering fake uninstall/redact flows for a victim shop, or other cross-tenant state corruption — all without needing the victim's credentials.

### Likelihood Explanation
Any developer who has the app installed on their own (attacker-controlled) shop trivially has legitimate access to `(raw_body, hmac)` pairs signed with the shared `api_secret_key`. No `api_secret_key`, access token, or privileged account for the *victim* shop is required — only unprivileged access to a normal, attacker-owned shop installation of the same app, which is the baseline assumption for any Shopify public app. The attack requires no timing race, MITM, or social engineering.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body — e.g., include the `shop-domain` header in `to_signable_string`, or require host apps to compare `request.shop` against session state for a shop that is independently known/authorized before trusting the identity. At minimum, document prominently that `request.shop`/`WebhookMetadata.shop` is unauthenticated and must not be used as the sole tenant key without corroboration.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, and captures a legitimate webhook delivery, e.g., a `products/update` payload `body = '{"id":1,...}'` with its accompanying `x-shopify-hmac-sha256` header (valid because both are produced with the app's shared `api_secret_key`).
2. Attacker crafts a new POST to the app's public webhook endpoint using the same `raw_body` and `hmac`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers into `Request#shop` = `"victim-shop.myshopify.com"`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the shared secret (`lib/shopify_api/utils/hmac_validator.rb` lines 12-31; `lib/shopify_api/webhooks/request.rb` lines 35-38).
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host application processes/stores this attacker-controlled payload as belonging to the victim shop.

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
