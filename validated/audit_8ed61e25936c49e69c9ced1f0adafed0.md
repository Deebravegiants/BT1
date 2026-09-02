Based on my analysis, I found a valid vulnerability analog in the webhook processing code.

### Title
Cross-tenant webhook data injection via HMAC that does not cover the `shop` identity header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's webhook handler directly from an HTTP header, while the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies covers only the raw request body. Because the shop identity is not bound to the signature, a valid `(body, hmac)` pair captured from a legitimate webhook delivery for one shop can be replayed with a different `shop-domain` header and will still pass validation, letting the data be attributed to a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-controllable HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against `to_signable_string`, i.e. the body: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` after only checking the HMAC of the body, and forwards it unauthenticated into `WebhookMetadata`, which apps use to route/persist per-tenant data: [4](#0-3) 

The equality the gem implicitly assumes is: `hmac_verified_bytes == identity_bytes_acted_on`. In reality `hmac_verified_bytes = raw_body` while `identity_bytes_acted_on = header["shopify-shop-domain"]`, so the two are disjoint. An attacker who legitimately owns any Shopify store can subscribe a webhook to their own server, capture a genuine `(raw_body, x-shopify-hmac-sha256)` pair Shopify signs for their own shop's events, and replay that exact body/HMAC to the target app's webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the untouched body, and `Registry.process` passes the forged `shop` straight to the app's handler as if it were authentic.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to guarantee: an unprivileged internet user who merely operates their own Shopify store (no special access to the victim's shop, no access token, no `client_secret`) can inject webhook payloads that a multi-tenant app will process and persist as belonging to a different, victim shop. Depending on the app's handler logic, this enables cross-tenant data corruption/injection (e.g., forging fake "orders/create" or "app/uninstalled" events attributed to another merchant), which maps to the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likely and practically reachable: creating a Shopify development/partner store is free and requires no privileges, webhook subscriptions can be pointed at attacker-controlled infrastructure to capture legitimate `(body, hmac)` pairs, and replaying an HTTP POST with a modified header is trivial. The only work required is capturing one valid signed payload for a controlled shop, which any developer/tester account can do.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is actually verified — either by including the relevant Shopify headers in the signable string before computing the HMAC comparison, or by having the app-facing API require the caller to supply the expected shop domain and reject the request if it doesn't match a shop the app has an active session/webhook registration for. At minimum, document prominently that `request.shop`/`request.topic` are not authenticated by `HmacValidator.validate` and must not be trusted for tenant routing without additional verification (e.g., cross-checking against the app's stored session data for that specific webhook subscription).

### Proof of Concept
```ruby
# Attacker owns shop "attacker.myshopify.com" and has a legitimate webhook subscription.
# Shopify sends a real signed webhook for the attacker's own shop:
raw_body = '{"id": 1, "note": "legit order on attacker shop"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker.myshopify.com", # captured legitimately
}

# Attacker replays the SAME body+hmac to the target app's public webhook endpoint,
# only changing the shop-domain header to the victim's shop:
forged_headers = headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (it only checks raw_body),
#    and the handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
#    even though Shopify never sent this event for victim-shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
