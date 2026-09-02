### Title
Webhook `shop-domain` (and `topic`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification, while the `shop` (and `topic`) values that `ShopifyAPI::Webhooks::Registry.process` hands to application webhook handlers are read from unauthenticated HTTP headers. This breaks the identity binding: *bytes verified* (raw body) ≠ *bytes acted on* (shop-domain header used to attribute the event to a tenant).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC only against `verifiable_query.to_signable_string`, i.e. the raw body: [3](#0-2) 

`Registry.process` checks that HMAC (body-only) and, on success, immediately trusts `request.shop` and `request.topic` (header-only, unauthenticated) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the signature check never covers the `shop-domain` header, any HMAC that is valid for a given raw body remains valid no matter what shop-domain header is attached to it. An attacker who legitimately installs the app on their own shop will receive real webhooks — valid `(raw_body, hmac)` pairs computed with the app's `api_secret_key` — for their own shop's events. They can capture such a pair and replay the exact same body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header with a victim shop's domain. `Utils::HmacValidator.validate` will still succeed (it only checks the body), and `Registry.process` will invoke the handler believing the event legitimately originated from the victim shop, since `WebhookMetadata#shop` is populated straight from the spoofed header.

### Impact Explanation
This is the exact "field acted on but not covered by the HMAC" analog called out in the rules. Any app that uses `request.shop`/`WebhookMetadata#shop` to key persistence, session lookups, or trigger shop-scoped side effects (which is the documented and intended usage pattern of this field) can be made to attribute attacker-controlled payload data to an arbitrary victim shop domain, resulting in cross-tenant data injection/corruption in the host application. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Any actor who can install the app on a shop they control (a normal, unprivileged onboarding flow requiring no special credentials, leaked secrets, or access tokens) can obtain valid `(body, hmac)` pairs for webhooks addressed to their own shop, then simply resend the same bytes with a different `shop-domain`/`topic` header value. No knowledge of `api_secret_key` or any access token is required — only observation of legitimate webhook deliveries the attacker already receives for their own tenant.

### Recommendation
Include the `shop`, `topic`, and any other header-derived identifiers that are trusted downstream in the HMAC-covered signable string (or otherwise cryptographically bind them to the body, e.g. by hashing headers+body together the way Shopify's own webhook payloads increasingly include shop/topic context), or require host applications to independently validate the `shop` domain against known installed shops before trusting `WebhookMetadata#shop`. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are *not* authenticated by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives a legitimate webhook delivery:
#   raw_body = '{"id":123,"note":"hello"}'
#   headers  = {
#     "x-shopify-topic" => "orders/create",
#     "x-shopify-hmac-sha256" => "<valid HMAC of raw_body computed with app secret>",
#     "x-shopify-shop-domain" => "attacker.myshopify.com"
#   }

# Attacker replays the SAME body+hmac, but swaps the shop-domain header:
spoofed_headers = headers.merge(
  "x-shopify-shop-domain" => "victim-shop.myshopify.com"
)

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)

# HMAC validation still passes because it only checks raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process will invoke the handler believing this event came from victim-shop:
ShopifyAPI::Webhooks::Registry.process(request)
# handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: {...attacker data...})
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
