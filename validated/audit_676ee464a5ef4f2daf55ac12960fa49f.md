### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) Identity Fields Are Not Covered by HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the tenant-identifying `shop` field (read from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is never part of the signed payload. `ShopifyAPI::Utils::HmacValidator` then verifies `hmac == HMAC(secret, raw_body)`, so the equality actually enforced is `bytes_verified == raw_body`, not `bytes_verified == (shop, raw_body)`. Any request whose body/HMAC pair is valid will pass validation regardless of what `shop`, `topic`, or `webhook_id` header values are attached to it.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic binding to the signed content: [2](#0-1) 

`HmacValidator.validate` verifies the signature purely against `to_signable_string` (i.e., the raw body): [3](#0-2) 

`Registry.process` then dispatches the handler with the `shop` value taken directly from this unverified header field, as shown by the test asserting `data.shop == @shop` while the HMAC covers only the JSON body `"{}"`: [4](#0-3) 

Because the `shop` (and `topic`/`webhook_id`) headers are excluded from `to_signable_string`, the identity binding an app relies on — "the HMAC-verified bytes correspond to *this* shop's webhook" — does not hold. The equality actually checked is:

`compute_signature(raw_body, secret) == received_hmac`

not

`compute_signature(raw_body + shop + topic, secret) == received_hmac`

An attacker who legitimately installs the app on their own store (an "unprivileged" actor with respect to any other tenant) will receive genuine webhook deliveries with valid `(raw_body, hmac)` pairs computed by Shopify using the app's real `api_secret_key`. Because that pair is not bound to the `shop-domain` header, the attacker can replay the exact same body/HMAC while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim shop's domain) when POSTing to the app's webhook endpoint. `HmacValidator.validate` still returns `true` because it only checks the raw body, and `Registry.process` passes the forged `shop` value on to the app's handler as if the event genuinely originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to provide via webhook processing: an app that keys any tenant-scoped side effect (record updates, session/token lookups, billing/entitlement changes, audit logs) off `Webhooks::Request#shop` can be made to associate attacker-controlled webhook content with a different (victim) shop. This is a cross-tenant confusion vector reachable purely by an internet user who can install the app on any store (no elevated Shopify credentials, no leaked secrets, no TLS interception needed) and observe/replay their own legitimate webhook deliveries with a spoofed header.

### Likelihood Explanation
The attack requires no privileged access: any merchant who installs the app can capture real webhook deliveries destined for their own store (valid body + HMAC), and only needs to alter an unauthenticated header (`shopify-shop-domain`) when replaying the request to the app's public webhook endpoint. The gem provides no mechanism to detect this because `shop` is deliberately excluded from the signable string.

### Recommendation
Include the tenant-identifying fields (`shop`, and ideally `topic`/`webhook_id`) in the HMAC-signable string, or otherwise cryptographically bind them to the verified payload, so that `HmacValidator.validate` can only succeed for the exact `(shop, body)` pair Shopify actually signed. At minimum, document and/or enforce that consuming applications must independently corroborate `Request#shop` against a known/installed-shop list before treating a processed webhook as authoritative for that shop.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real event (e.g., updates a product) that causes Shopify to send a legitimate webhook to the app's endpoint with body `B` and header `shopify-hmac-sha256: HMAC(secret, B)` and `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures this request (e.g., via a proxy on infrastructure they control, or by having the app log/forward it).
3. Attacker replays the identical body `B` and HMAC header to the same endpoint, but changes `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `#shop`, `HmacValidator.validate` succeeds because it only checks `HMAC(secret, B)` against the unchanged body `B`: [5](#0-4) 
5. `Registry.process` invokes the handler with `shop == "victim-shop.myshopify.com"`, causing the host application to attribute attacker-controlled webhook content to the victim tenant.

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

**File:** test/webhooks/registry_test.rb (L271-298)
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
```
