### Title
Webhook `shopify-shop-domain` and `shopify-topic` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` and `topic` values that are handed to the app's webhook handler are read straight from HTTP headers that are never included in the signed material. Because `Context.api_secret_key` is a single per-app secret shared across every merchant installation (not a per-shop secret), any merchant who has installed the app can obtain a genuinely-signed webhook body and then replay it with a forged `shopify-shop-domain`/`shopify-topic` header pair, causing the app to process attacker-supplied data as if it originated from a different tenant.

### Finding Description
`Request#hmac` and `Request#to_signable_string` bind the signature strictly to `@raw_body`: [1](#0-0) [2](#0-1) 

But `shop` and `topic`, which are used to route and identify the tenant for the webhook payload, are parsed directly out of unauthenticated headers with no cryptographic tie to the body/signature: [3](#0-2) 

`HmacValidator.validate` (used the same way for both OAuth callback and webhook verification) only ever checks the `to_signable_string` value against the secret — it has no way to bind out-of-band fields like `shop`: [4](#0-3) 

The registry's `process` method passes `request.shop`/`request.topic` through to the app's registered handler as the tenant identity for the delivered data, as confirmed by the test asserting `data.shop == @shop` after processing a request built from arbitrary headers plus a body-only HMAC: [5](#0-4) 

This breaks the intended identity binding: **shop value verified by the HMAC == shop value delivered to the handler**. Since the app's `api_secret_key` is shared across all shops that install the app (it is the app's client secret, not a per-installation secret), an attacker who runs their own shop installation can capture a real, validly-signed webhook (body + HMAC) sent to their own endpoint, and resend that exact body/HMAC pair to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still passes (it only checks the body), and the handler receives forged data purportedly belonging to another tenant.

### Impact Explanation
This allows a malicious merchant to make the host application process forged, adversary-controlled webhook payloads under the identity of a different (victim) shop — a cross-tenant identity confusion condition traceable directly to `Request#shop`/`Request#topic` not being covered by `to_signable_string`.

### Likelihood Explanation
Any user who can install the app on their own store can obtain a legitimately-signed webhook body (since the same `api_secret_key` signs webhooks for every installation), then only needs to modify the `shopify-shop-domain` (and optionally `shopify-topic`) header before replaying it to the public webhook endpoint the host application exposes. This is a purely unprivileged, low-effort forgery, no access to a victim's credentials or the app's actual `client_secret` value is needed.

### Recommendation
Include `shop` (and `topic`, `webhook_id`, `api_version` where used for routing/attribution) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind those header values to the payload before trusting them in `Registry.process`. Alternatively, document/require that host applications cross-check `request.shop` against a shop known to be installed and independently validate topic/shop consistency before acting on webhook data, since the gem's own signature check does not protect these fields.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures a public HTTPS webhook endpoint that forwards to their own app.
2. Shopify sends a legitimate webhook: body `B`, `shopify-hmac-sha256: HMAC(api_secret_key, B)`, `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends this exact `B` and HMAC value to the target app's public webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — validation succeeds.
5. The registered handler receives `data.shop == "victim-shop.myshopify.com"` (per `test/webhooks/registry_test.rb:271-301` behavior) even though the payload actually originated from the attacker's own shop, resulting in forged, cross-tenant webhook data being processed by the app.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L16-28)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** test/webhooks/registry_test.rb (L271-301)
```ruby
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
