### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while `topic`, `shop`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers and passed downstream as if verified. This breaks the identity binding `HMAC(signed bytes) == HMAC(bytes acted on)` in exactly the same way the reported `collectedEther` bug broke `msg.value == amount credited`: the gem verifies one thing (the body) but acts on a different, uncovered thing (the shop-identifying headers).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies the HMAC over that signable string (i.e., over the body only) and then trusts `request.shop`/`request.topic`/`request.webhook_id`/`request.api_version` to build `WebhookMetadata`, which is handed to the app's handler as authenticated data: [3](#0-2) 

The `HmacValidator` itself only ever checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, so it has no visibility into headers at all: [4](#0-3) 

The identity binding that should hold is: `shop attributed to this event == shop that produced the signed body`. Because `shop-domain` (and `topic`/`webhook_id`) is outside the signed bytes, that equality can be broken: any request with a *body+HMAC pair from a legitimately-received webhook* remains "valid" regardless of what shop-domain header accompanies it. This is documented as the trusted identity for handlers — the gem's own docs tell app authors to key business logic off `data.shop`: [5](#0-4) [6](#0-5) 

### Impact Explanation
An unprivileged internet user can install the app on their own (attacker-controlled) shop, receive a genuine webhook delivery to their own endpoint, and thereby obtain a valid `(raw_body, HMAC)` pair signed with the app's `client_secret` — without ever learning the secret itself. They can then replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header for a victim merchant's domain. `Registry.process` will accept the HMAC as valid (it only checks the body) and dispatch `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the handler. Any app that uses `data.shop` to select which merchant's records to update — which is exactly what the gem's own documentation instructs — will act on the victim tenant using attacker-supplied data, i.e. cross-tenant access/data corruption.

### Likelihood Explanation
Requires only: (1) the attacker's ability to run a normal, unprivileged app installation to capture one legitimate `(body, HMAC)` pair for any topic they care to spoof, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint (no auth needed there by design). No access token, `client_secret`, or privileged account is required. This is a straightforward, deterministic replay — likelihood is high once an attacker understands the header/body decoupling.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the request (e.g., require the host app to independently verify `shop` came from a shop with an active, registered webhook subscription/session before trusting it). At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be used as a sole tenant-selection key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` value `H` (computed by Shopify over `B` with the app's shared secret).
2. Attacker POSTs to the app's public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (valid, since HMAC only covers `B`), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers (`lib/shopify_api/webhooks/request.rb:45-63`); `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:13-22`).
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and, following the gem's documented pattern, updates records for `victim-shop.myshopify.com` using attacker-supplied body content.

### Citations

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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
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
