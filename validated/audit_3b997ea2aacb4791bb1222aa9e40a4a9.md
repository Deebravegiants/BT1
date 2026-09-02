### Title
Webhook HMAC only signs `raw_body`, not `shop-domain`/`topic`/`webhook-id`/`api-version` headers, enabling cross-tenant webhook impersonation via replay - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` as authenticated once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC only ever covers the raw body bytes. Because the app's `api_secret_key` is shared across every shop that installs the app, an attacker who legitimately receives one valid `(body, hmac)` pair for their own dev-shop install can replay that exact body/hmac pair to the same app's public webhook endpoint with arbitrary `shop-domain`, `topic`, `webhook-id`, and `api-version` headers, and the gem will accept and dispatch it as if it were an authentic event for the victim shop/topic.

### Finding Description
The claimed binding is: `HmacValidator.validate(request) == true` should imply `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` are authentic for the bytes that were verified. This binding does not hold.

`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All of the header accessors (`shop`, `topic`, `webhook_id`, `api_version`) are pulled straight from the unauthenticated HTTP headers via `shopify_header`, and are never mixed into the signable string: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received `hmac` header — it never touches shop/topic/webhook-id/api-version: [4](#0-3) 

`Registry.process` only gates on this body-only HMAC check, then immediately trusts `request.topic`, `request.shop`, `request.webhook_id`, `request.api_version` for dispatch, with no nonce, timestamp, or webhook-id uniqueness/replay check: [5](#0-4) 

**Attacker's exact request and exploit flow:**
1. The attacker (per the rules, allowed to create their own dev shop and install the target app) triggers a genuine webhook delivery to their own registered endpoint for any topic (e.g. `products/update`), optionally shaping the JSON body content by manipulating their own store's data before triggering it.
2. The attacker's own server receives the real `raw_body` and `x-shopify-hmac-sha256` value. This HMAC is computed with the app's `api_secret_key`, which is the same secret used for every shop that installs the app — the attacker never needs to know the secret itself, only a valid `(body, hmac)` pair produced under it.
3. The attacker then sends a new POST directly to the target app's public webhook receiving endpoint, reusing the exact captured `raw_body` and `x-shopify-hmac-sha256`, but swapping `x-shopify-shop-domain` to the victim shop, and optionally `x-shopify-topic`/`x-shopify-webhook-id`/`x-shopify-api-version` to any values (as long as a handler is registered for the chosen topic).
4. `HmacValidator.validate` recomputes `HMAC(secret, raw_body)` — unchanged since the body wasn't touched — and it matches the received hmac, so `Registry.process` proceeds and calls the registered handler with `shop: request.shop` (now the victim's domain) and `topic`/`webhook_id`/`api_version` all attacker-chosen.

None of the existing guards catch this: `HmacValidator.validate` only checks body integrity/authenticity under a key shared across all tenants of the app, not identity binding; there is no `state`/nonce/timestamp check in the webhook path (that only exists in OAuth flows); `ShopValidator`, `JwtPayload`, `Context.setup?`/`private?`/`embedded?` are unrelated to this webhook code path.

### Impact Explanation
Per delivery, an attacker can make the host application's webhook handler execute believing an event came from an arbitrary victim shop and/or an arbitrary registered topic, using only a body they legitimately obtained a signature for from their own tenant. This is a forged-webhook authentication bypass and cross-tenant impersonation: any app logic that trusts `WebhookMetadata#shop`/`#topic` (e.g., to update per-merchant records, trigger data deletion for `customers/redact`/`shop/redact`, or credit/state changes keyed by shop) can be invoked against a shop the attacker does not control. This is repeatable against arbitrary victim shop domains and arbitrary registered topics, limited only by whatever body content the attacker was able to legitimately capture/shape for themselves. This matches the Critical category: authentication bypass (forged webhook accepted) / cross-tenant access.

### Likelihood Explanation
Preconditions: the host app must register at least one HTTP webhook handler via `Registry.add_registration` (already assumed as documented usage) and expose the webhook endpoint publicly (webhook endpoints inherently must be internet-reachable for Shopify to call them). The attacker only needs to be able to install the app on a shop they control and capture one genuine webhook delivery — both explicitly permitted under the stated attacker capabilities. No secrets, TLS interception, or privileged access are required, and the attack is trivially repeatable and low-cost (a single HTTP POST with modified headers, reusing a captured body/hmac pair).

### Recommendation
Bind the delivery's identity to the signed material, e.g. include `shop-domain`, `topic`, and `webhook-id` (in addition to the body) in the signable string/verification, or otherwise verify the shop/topic against Shopify's IP allowlist/mTLS if available, and add webhook-id-based replay protection (track processed `webhook_id`s and reject duplicates/reused ids across shops).

### Proof of Concept
```ruby
# test/webhooks/registry_replay_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class RegistryReplayTest < Test::Unit::TestCase
      def test_replayed_body_with_swapped_shop_header_is_accepted
        raw_body = '{"id":1,"title":"attacker-controlled"}'
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          raw_body,
        )
        original_headers = {
          "x-shopify-topic" => "products/update",
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
          "x-shopify-webhook-id" => "orig-id",
          "x-shopify-api-version" => "2024-01",
        }
        original_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: original_headers)
        assert(ShopifyAPI::Utils::HmacValidator.validate(original_request))

        # Attacker swaps only headers, keeps raw_body + hmac identical
        forged_headers = original_headers.merge(
          "x-shopify-shop-domain" => "victim-shop.myshopify.com",
          "x-shopify-webhook-id" => "replayed-id",
        )
        forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

        # Same raw_body/hmac => still validates, even though "shop" is now the victim's
        assert(ShopifyAPI::Utils::HmacValidator.validate(forged_request))
        assert_equal("victim-shop.myshopify.com", forged_request.shop)
        assert_equal(original_request.hmac, forged_request.hmac)

        handler_called_with = nil
        handler = TestHelpers::FakeWebhookHandler.new(
          lambda { |data| handler_called_with = data },
        )
        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "products/update", path: "path", delivery_method: :http, handler: handler,
        )

        ShopifyAPI::Webhooks::Registry.process(forged_request)

        # Registry.process dispatched to the handler AS the victim shop, using a replayed signature
        assert_equal("victim-shop.myshopify.com", handler_called_with.shop)
      end
    end
  end
end
```
This asserts both sides of the claimed binding explicitly: `HmacValidator.validate` returns true for both the original and the header-swapped request (body/hmac equality), while `request.shop` differs between them — demonstrating that HMAC validity does not bind to the shop/topic headers that `Registry.process` trusts for dispatch.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
