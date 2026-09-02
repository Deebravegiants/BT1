### Title
Webhook HMAC validation only covers the request body, not the `shop-domain`/`topic` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` authenticates the *body bytes* but never binds the `shop-domain` or `topic` headers to that signature. `Registry.process` then trusts `request.shop` and `request.topic` — taken straight from unauthenticated headers — to route the payload and populate `WebhookMetadata`. This breaks the identity binding `HMAC-verified-bytes == tenant-attributed-bytes`: an attacker who can produce any one valid `(body, hmac)` pair (e.g., by installing the app on their own store and capturing a webhook with a body that carries no shop-specific data, such as an empty-body event) can replay that exact body+HMAC pair against the app's webhook endpoint with an arbitrary `shop-domain`/`topic` header, and the signature still validates.

### Finding Description
The signable content for a webhook request is defined as just the raw body: [1](#0-0) 

`HmacValidator.validate` verifies the HMAC strictly over `verifiable_query.to_signable_string`: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers on the `Request` object and are never part of the HMAC input: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts these unauthenticated header values to select the handler and build the metadata object that the host application's business logic acts on: [4](#0-3) 

Because the `api_secret_key` is shared by the app across *all* installed shops (it is not per-tenant), any merchant who installs the app on their own store is an "unprivileged internet user" from the perspective of any other tenant, yet they can generate a fully valid `(body, hmac)` pair for topics whose body content is shop-independent (e.g., `{}` payloads, or payloads with attacker-fully-controlled/shop-independent fields). That captured pair can then be POSTed directly to the app's webhook endpoint with a forged `shop-domain` header naming a victim shop and/or a forged `topic` header, and `HmacValidator.validate` will accept it because the signature never covered those header values in the first place.

### Impact Explanation
This breaks the intended binding "the shop/topic that the HMAC-authenticated payload actually pertains to" == "the shop/topic value the application acts upon." A host application built on `Registry.process`/`WebhookMetadata` cannot distinguish a genuine webhook from shop A from a forged one merely relabeled as shop A, which is a cross-tenant integrity failure: attacker-controlled (or replayed) data can be attributed to and processed against a victim tenant's context (e.g., triggering handlers such as `app/uninstalled`, `customers/redact`, or order/inventory handlers keyed only by `WebhookMetadata.shop`), even though that shop never actually sent it.

### Likelihood Explanation
Exploitation requires the attacker to (1) control at least one shop install to legitimately obtain one valid `(body, hmac)` pair — trivial and unprivileged, since anyone can install a public app on a dev/test store — and (2) find or force a topic/body combination with no shop-identifying content inside the body itself (common, since many webhook payloads carry little to no shop-specific data, or the shop information the handler cares about is exactly the header value being forged). No secret material, TLS interception, or privileged account is required.

### Recommendation
Include the `shop-domain` and `topic` header values (and any other header the application relies on for identity/routing) inside the signed material used by `HmacValidator`, or otherwise independently verify that the `shop-domain` header matches a shop known to have installed the app and is consistent with the topic/payload before dispatching to a handler. At minimum, `Request#to_signable_string` should be documented/extended so that consumers cannot mistake `HmacValidator.validate` as authenticating the shop/topic headers.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook for a topic with an empty/generic body, e.g. `raw_body = "{}"`, together with the valid `x-shopify-hmac-sha256` header computed by Shopify using the app's shared `api_secret_key`.
2. Attacker sends their own POST request directly to the app's webhook endpoint, reusing the exact `raw_body` and `hmac` header, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: <topic of attacker's choice>`
3. `ShopifyAPI::Webhooks::Request.new` parses these headers into `shop`/`topic`, and `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only ever contained `raw_body`, which is unchanged.
4. `Registry.process` dispatches to the handler registered for the forged `topic`, calling it with `WebhookMetadata.new(topic: <forged>, shop: "victim-shop.myshopify.com", body: {}, ...)` — the host application now processes an event attributed to `victim-shop.myshopify.com` that never originated from that shop. [4](#0-3) [5](#0-4) [6](#0-5)

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
