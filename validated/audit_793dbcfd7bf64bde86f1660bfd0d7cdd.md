Confirmed root cause: the webhook `Request.shop` value is read straight from an HTTP header and is never included in the HMAC-signed material.This confirms the identity binding break: `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` only checks `verifiable_query.to_signable_string` against the HMAC, and `Webhooks::Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` returns only `@raw_body` — the `shop` (and `topic`/`webhook_id`/`api_version`) values, which come from `shopify_header("shop-domain")`, are completely outside the signed material yet are trusted and forwarded to the app's handler as the tenant identifier.

### Title
Webhook `shop` (tenant) identity is read from an unauthenticated header and never covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#shop` is derived solely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but `Request#to_signable_string` (the value the gem HMAC-verifies) only returns the raw request body. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, which apps are documented to use as the tenant key for persisting/looking up data.

### Finding Description
`Registry.process` performs: [1](#0-0) 

The HMAC check is `Utils::HmacValidator.validate(request)`, which calls `validate_signature`, comparing the computed HMAC of `verifiable_query.to_signable_string` to the received `hmac`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body, and `hmac` is read from the `hmac-sha256` header — neither includes the shop domain: [3](#0-2) [4](#0-3) 

So the equality the gem is supposed to enforce is:
`shop authenticated by HMAC == shop passed to the app's tenant-scoped handler`

but what is actually enforced is only:
`HMAC(body, secret) == received_hmac`

`shop` is read from an attacker-controllable header field with **no cryptographic binding** to the signature at all. Since the merchant's own webhook deliveries for their own store are legitimate HTTP requests hitting the app's public webhook endpoint (an unprivileged internet actor can operate their own trial/dev shop and install the target app to receive real, validly-signed webhooks for known, attacker-chosen bodies such as `orders/create`/`app/uninstalled` with empty or attacker-influenced content), the attacker can capture a `(raw_body, hmac)` pair that is valid for the secret, then replay it to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. The HMAC still validates (it only signs `raw_body`), and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, ...)` — i.e., the victim's shop — to the handler, which per the gem's own documented usage pattern is what apps key their per-tenant data operations on: [5](#0-4) [6](#0-5) 

This is the same bug class as the referenced report: a value (`cumulativeCashflowApr`/here `shop`) is combined/consumed in a downstream computation while the cryptographic guard (smoothing-period check / HMAC) that is supposed to bound it does not actually cover that value, letting attacker-controlled input flow through the "verified" path unchecked.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook processing: the shop identity delivered to the app-provided `WebhookHandler` for persistence, lookups, or action is not authenticated at all, letting an attacker who controls only their own (attacker-owned) shop craft/replay requests that appear scoped to a victim's shop with a cryptographically "valid" webhook. Any app that follows the gem's own documented pattern of trusting `data.shop` for tenant-scoped writes/reads (e.g., updating order/product records, revoking access on `app/uninstalled`, billing state) is exposed to cross-tenant data corruption or disclosure — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
High: the attack requires no secrets, no privileged access, and no TLS interception — only an internet-reachable app webhook endpoint (which is by design public) and a validly-signed webhook the attacker can obtain via their own legitimate install of the app (or any other shop's already-observed webhook, since request bodies/topics are often predictable, e.g. `app/uninstalled` with an empty body). The gem provides no field, warning, or verification step tying `shop` to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook_id) in the HMAC-signed material, or otherwise cryptographically bind the `shop-domain` header to the verified request (e.g., verify shop against a known/registered shop list or session store before trusting it), instead of relying on Shopify to always send header values that match a signature that never covers them. At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be used as a sole tenant key without additional verification (e.g., cross-checking against an existing stored session for that shop).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `app/uninstalled` with raw body `{}` and a valid `x-shopify-hmac-sha256` computed by Shopify over that body with the app's real secret.
2. Attacker replays the exact same raw body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(raw_body, secret) == hmac` — the shop header is never part of the signed input (see [4](#0-3) ).
4. `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` with `shop == "victim.myshopify.com"` and invokes the app handler, which (per the gem's documented usage) acts on `victim.myshopify.com`'s data as if Shopify had genuinely notified the app about that shop.

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

**File:** docs/usage/webhooks.md (L10-26)
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
```
