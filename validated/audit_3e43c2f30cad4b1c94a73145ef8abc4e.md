Based on my investigation, I found a genuine identity-binding gap in the webhook verification path.

### Title
Webhook shop-domain header not covered by HMAC signature, allowing tenant spoofing in processed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body [1](#0-0) , while the `shop` value used by callers as the tenant/session key is read from a separate, unsigned HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`) [2](#0-1) .

### Finding Description
`HmacValidator.validate` verifies the webhook by comparing `hmac` (decoded from the `hmac-sha256` header) against a signature computed over `to_signable_string`, which is just `@raw_body` [3](#0-2) [4](#0-3) . The `shop` accessor used to identify which tenant/shop the webhook belongs to comes from a plain header lookup with no cryptographic binding to the signed bytes [2](#0-1) [5](#0-4) . The identity binding this breaks is: `shop_used_for_dispatch == shop_covered_by_hmac`, which does not hold here since only the body bytes are signed, not the `shop-domain` header.

This means a legitimate, validly-signed webhook body from Shopify (any tenant's webhook, including one the app's own developer could obtain, e.g., a test/trial store the "attacker" controls) can be replayed with a rewritten `shopify-shop-domain` header pointing at a victim shop, and it will still pass `HmacValidator.validate` because the HMAC never covered that header.

### Impact Explanation
Downstream, `Registry.process` uses this unauthenticated `shop` value to route the payload to a handler as if it belongs to that shop (see test scaffolding demonstrating `data.shop` being derived directly from the header) [6](#0-5) . Any app that keys business logic (e.g., session/token lookup, data writes) off `Webhooks::Request#shop` is exposed to cross-tenant data confusion: an attacker who owns a valid app installation (so they can generate a validly-HMAC-signed webhook for their own shop) can forge the shop-domain header value to impersonate a different, victim shop when submitting the (replayed) request directly to the app's webhook endpoint — bypassing the tenant boundary the HMAC is supposed to guarantee.

### Likelihood Explanation
Medium: the webhook endpoint is a public HTTP endpoint, and the attacker needs only one legitimately-signed webhook body from Shopify (obtainable via their own app installation/store) to replay with a modified header, since header spoofing is trivial for an unprivileged internet user posting directly to the app's public webhook URL (bypassing Shopify's TLS-terminated proxy headers is exactly what the header claims are meant to prevent, but the HMAC doesn't cover them).

### Recommendation
Bind the `shop` (and `topic`, `webhook_id`, `api_version`) values into the signed content actually verified — e.g., include them in `to_signable_string`, or require the host app to independently verify shop identity via a trusted, separately-authenticated channel (such as matching against a known session/shop already established via OAuth) before trusting `Request#shop`. At minimum, document prominently that `shop`, `topic`, etc. are not covered by HMAC verification and must not be trusted for tenant routing without additional authentication.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook POST from Shopify for some topic, with a valid `hmac-sha256` header computed over the JSON body.
2. Attacker replays this exact request directly to the app's public webhook endpoint but rewrites the `shopify-shop-domain` header to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` still passes because it only recomputes/compares the HMAC over `@raw_body` [1](#0-0) ; the forged `shop-domain` header is never part of the signed bytes.
4. `Registry.process` dispatches the handler with `data.shop == "victim.myshopify.com"` [7](#0-6) , causing the app to act on/attribute the (attacker-controlled) payload to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** test/webhooks/registry_test.rb (L271-299)
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
```
