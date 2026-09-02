### Title
Webhook shop identity (`Webhooks::Request#shop`) is trusted for tenant identification while HMAC verification only covers the raw body, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), `topic`, and `webhook_id` from unauthenticated HTTP headers, while `Utils::HmacValidator.validate` (invoked from `Registry.process`) only verifies the HMAC over the request body. This breaks the intended identity binding `hmac_signed_bytes == bytes_the_app_acts_on`, since the `shop` value that `Registry.process` hands to the host app's handler is never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and this is the only value verified by `Utils::HmacValidator.validate`, which computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` header via `OpenSSL.secure_compare` [2](#0-1) .

However, `Request#shop`, `#topic`, and `#webhook_id` are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) with no cryptographic binding to the signed body [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` struct that is handed to the host application's `WebhookHandler#handle`: [4](#0-3) . The resulting `WebhookMetadata` exposes `shop` as a plain `String` field with no further validation [5](#0-4) .

Because the HMAC only signs the body, an attacker who legitimately owns any Shopify store can capture one genuine `(raw_body, hmac)` pair delivered to their own webhook endpoint (e.g. by subscribing their own store to a webhook topic), and then replay that exact body+HMAC pair directly to the target app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header value. `Utils::HmacValidator.validate` still returns `true` because the body is unchanged, yet `request.shop` now returns the attacker-chosen shop domain, which `Registry.process` passes on to the app's handler as the authoritative tenant identity.

### Impact Explanation
Any host application that relies on `WebhookMetadata#shop` (the documented, gem-provided value) to determine which tenant/merchant a webhook event belongs to — e.g., to look up or mutate that merchant's stored session/access token, orders, or other tenant-scoped data — can be made to act on the wrong tenant's data using a request whose HMAC was computed under the attacker's own store's payload. This is a cross-tenant identity binding failure: `hmac(body)` is valid, but `shop` (the field acted upon) is not covered by that HMAC, exactly the class of "field acted on but not covered by the HMAC" flagged as in-scope. This can lead to cross-tenant access to webhook-triggered application logic under an attacker-chosen shop identity.

### Likelihood Explanation
Exploitation requires: (1) the attacker to legitimately install the app or otherwise obtain one genuine `(body, hmac)` pair for any shop (trivial — attacker can create a Shopify development/trial store and trigger any webhook topic against their own installation), and (2) the app's webhook endpoint to be reachable directly over the internet with attacker-controlled headers (true for any HTTP endpoint fronted by a normal web server/load balancer, since this gem does not mandate mTLS-restricted delivery from Shopify's IP ranges). No secret material is required. Likelihood is moderate-to-high for any app that trusts `WebhookMetadata#shop` for tenant-scoping without independent verification.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the material verified by the HMAC, or otherwise validate that `request.shop` corresponds to a shop with a stored, previously-established session/installation before using it, rather than trusting the header value returned unconditionally by `Registry.process`. At minimum, the gem should document/enforce that `WebhookMetadata#shop` must be cross-checked by the host app against a known-installed shop list, since it is presently unauthenticated header data despite superficially passing "HMAC validation."

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and subscribes to any webhook topic (e.g. `orders/create`).
2. Shopify delivers a genuine webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-SHA256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Attacker captures `(B, H)` from their own delivery (e.g. via a debugging proxy they control, since it's their own request).
4. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-SHA256: H` (unchanged, still valid for body `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (spoofed)
5. `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only covers `B` [1](#0-0) .
6. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , even though the event content actually originated from the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
