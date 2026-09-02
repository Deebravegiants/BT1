### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not bound to the HMAC signature, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values that the gem hands to application webhook handlers are taken from unauthenticated HTTP headers. The identity binding `shop_used_by_handler == shop_that_produced_the_signed_bytes` does not hold, because the signature never covers the shop header.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) are read straight from headers, which are attacker-controllable on the wire and are never part of the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies `hmac` against `to_signable_string` using the app's single `Context.api_secret_key`/`Context.old_api_secret_key` — this secret is shared across every shop that has installed the app, it is not shop-specific: [3](#0-2) 

Because the same `client_secret` is used to sign webhooks for every merchant, a `(raw_body, hmac)` pair that is valid for one shop is also cryptographically valid for any other shop — the signature proves "this body was produced by an app-secret holder," not "this body belongs to shop X." The `shop` field that downstream handlers use to decide tenant context (as shown in the test harness passing `data.shop` to handlers) is asserted only via the unauthenticated header: [4](#0-3) 

An attacker who operates their own Shopify store with the app installed can:
1. Trigger a legitimate webhook from their own shop, capturing the valid `raw_body` + `x-shopify-hmac-sha256` pair (both signed with the app's shared secret).
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to a victim shop's domain.
3. `HmacValidator.validate` still passes, because it only checks the raw body against the shared secret — it never checks that the body actually came from the shop named in the header.
4. `Registry.process` dispatches to the handler with `data.shop` = victim shop domain, while the actual payload content is fully attacker-controlled (from the attacker's own store's event).

This is the same identity-binding failure class as the reported Solidity bug (a check exists — `validateBalances()`/HMAC — but an unchecked mutation/field — `borrow()`/`shop` header — can move state after the check without re-validating the value the check is supposed to protect).

### Impact Explanation
This breaks the tenant boundary the gem is responsible for maintaining between shops (`shop_asserted_by_gem == shop_that_actually_signed_the_data`). An app that keys any data write, entitlement, or side effect off `Webhooks::Request#shop` / `data.shop` (which is the gem's documented intended usage) can be made to process attacker-supplied payloads under a victim shop's identity — cross-tenant access/data confusion, which the rules classify as Critical.

### Likelihood Explanation
Requires only an unprivileged internet user who can install the app for free on their own development store (a normal, unauthenticated action for any public/free-to-install app) and can send arbitrary HTTP requests to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is needed — only the ability to receive one legitimate webhook for their own shop and replay/relabel it.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed material, or independently verify that the shop in the header matches a shop known to be associated with the specific `webhook_id`/subscription before invoking handlers, rather than trusting `x-shopify-shop-domain` purely from an HMAC check that never covers it.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic to receive a real `POST` with body `B` and header `x-shopify-hmac-sha256: H` (`H = HMAC-SHA256(client_secret, B)`).
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim.myshopify.com", "shopify-hmac-sha256" => H})` is constructed; `HmacValidator.validate` still succeeds since it only hashes `B`.
4. `Registry.process` invokes the app's handler with `topic`, `body` (attacker-controlled), and `shop == "victim.myshopify.com"`, causing the handler to act on victim-shop data/state using attacker-supplied content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** test/webhooks/registry_test.rb (L266-301)
```ruby
      def test_process_with_new_format_headers
        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal("b1234-eefd-4c9e-9520-049845a02082", data.webhook_id)
            assert_equal("2024-01", data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)

        assert(handler_called)
```
