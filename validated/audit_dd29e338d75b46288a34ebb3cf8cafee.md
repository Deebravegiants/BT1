### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant spoofing of webhook origin - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request body, while the `shop` (tenant) identity that the documented handler API relies on is taken from an unauthenticated HTTP header. This breaks the identity binding: `shop_asserted_by_header == shop_that_produced_the_signed_body` is never checked.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` gates all further processing on this single check, then immediately builds `WebhookMetadata` using `request.shop`, which is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header without any cryptographic binding to the signed body: [3](#0-2) [4](#0-3) 

The documented handler contract explicitly instructs integrators to trust `data.shop` as the tenant identifier for dispatching work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), i.e., this is the gem's documented, intended usage, not host-application misuse: [5](#0-4) 

Because the HMAC only proves "this body was produced using the app's shared secret" and says nothing about which shop it was produced for, any attacker who can obtain one legitimately-signed webhook request (e.g., by installing the app on their own store — an unprivileged action) can replay that exact `raw_body` + valid `hmac` to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop's domain. `HmacValidator.validate` will still return `true` (it never inspects the header), and the handler will process attacker-controlled body content under the identity of the victim tenant.

### Impact Explanation
This matches the "field acted on but not covered by the HMAC" analog: `Registry.process` verifies bytes it does not act on the identity of (body only), while acting on a field (`shop`) it never verifies. Depending on how the host application uses `data.shop` (e.g., looking up the merchant/session or writing to shop-scoped storage using this value, per the documented pattern), this enables cross-tenant data poisoning/spoofing — an app could enqueue or persist attacker-supplied webhook content tagged as belonging to a shop the attacker doesn't control. This satisfies the "cross-tenant access" criterion for Critical severity.

### Likelihood Explanation
Exploitation requires only: (1) the attacker install the target app on their own store (no privileged access needed — this is the normal, expected flow for any merchant), (2) capture one legitimately Shopify-signed webhook request for a topic whose body is attacker-influenceable (e.g., `orders/create`, `carts/update`), and (3) replay it to the app's public webhook endpoint with a forged `shop-domain` header. No secret material, TLS interception, or privileged account is required — matching the "unprivileged internet user" threat model.

### Recommendation
Bind the shop identity into the authenticated material, or otherwise cryptographically tie the `shop-domain` header to the verified request:
- Include `shop`, `topic`, and `webhook_id` (or the full header set Shopify signs) in the value passed to `to_signable_string`/HMAC computation, matching Shopify's actual webhook verification contract, or
- Require the host application to independently confirm that the shop claimed in the header corresponds to an app installation this app is currently registered for that specific webhook subscription, before trusting `data.shop`.
- At minimum, document prominently that `data.shop` is not authenticated by the HMAC check and must not be used as a sole tenant-authorization signal.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (an ordinary merchant action).
2. Attacker triggers a webhook (e.g., updates a product to fire `products/update`) whose body content they control to some extent, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
3. Attacker replays this exact request to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — this still passes because the body was untouched. [6](#0-5) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-supplied `body`, and processes it as if it originated from the victim tenant.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
