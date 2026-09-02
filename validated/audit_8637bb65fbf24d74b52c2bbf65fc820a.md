The docs explicitly claim `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and the `data.shop` field is documented as "The shop domain of the webhook" [2](#0-1)  that handlers are expected to key persistence/multi-tenant logic on (`shop_domain: data.shop`) [3](#0-2) . This confirms the exploit path: the HMAC only signs the raw body, never the shop-domain header, so an attacker who owns a legitimate shop can forge a webhook that Shopify itself would deliver, then replay it with an arbitrary `shop-domain` header while keeping the same valid body+HMAC, causing the app to attribute it to a different tenant.

### Title
Webhook HMAC does not cover the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `Registry.process` validates the HMAC solely against that body [4](#0-3) [5](#0-4) . The `shop` field, which is exposed to handlers as the tenant identifier `data.shop` [6](#0-5) , is read straight from the `shop-domain` header [7](#0-6)  and is never included in the signable string. This breaks the identity-binding equality: `bytes verified by HMAC` != `bytes used to determine the shop/tenant`.

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is simply `@raw_body` [8](#0-7) [4](#0-3) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from unauthenticated HTTP headers [9](#0-8) . `Registry.process` only checks the HMAC before dispatching the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [10](#0-9) , so the `shop` value handed to the app-provided handler carries no cryptographic binding to the signed body.

Because a merchant/attacker can legitimately trigger webhooks for their own shop (e.g. by creating an order in a store they own/control), they possess a body + valid HMAC pair signed with the app's real `client_secret`. Since headers are not part of the signed material, the attacker can freely swap the `shop-domain` header to any other shop domain (real or fabricated) while keeping the original body and HMAC intact — `HmacValidator.validate` will still return `true` because it only re-derives the HMAC from `@raw_body`.

### Impact Explanation
Any host application that follows this gem's documented pattern of persisting or acting on webhook data keyed by `data.shop` (as the README/`docs/usage/webhooks.md` explicitly recommends: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be tricked into writing/mutating data associated with a shop the attacker does not own, i.e., a cross-tenant data injection into another merchant's records — using only the credentials of the attacker's own, legitimately-installed shop. This satisfies the "cross-tenant access" criteria since the identity used for tenant-scoping (`shop`) is unauthenticated relative to what's cryptographically verified (the body).

### Likelihood Explanation
Likelihood is high for any app author following the gem's documented instructions verbatim, since the gem provides no additional safeguard (e.g., verifying `shop` is in the set of known/installed shops, or including the header in the signable string) and its own docs state the shop domain is a trusted webhook attribute. An attacker only needs to own or control an app-installed shop to obtain a valid `(body, hmac)` pair and can freely swap the shop header on replay, requiring no access to `api_secret_key` or any access token.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook_id`) header value in the signable string used for HMAC verification, or independently verify that the shop asserted in the header matches a shop the app has installed/has an active session for before dispatching to the handler. At minimum, document prominently that `data.shop` is not covered by the HMAC and must not be trusted as an authenticated tenant identifier without additional verification.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has the app installed there,
# so Shopify legitimately sends this webhook with a valid HMAC computed over the body.
raw_body = '{"id": 1, "note": "hello"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), real_api_secret_key, raw_body)

# Attacker crafts a request reusing the same body + hmac, but swaps the shop header
# to a victim shop domain the attacker does NOT control.
spoofed_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),  # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because it only checks raw_body against the HMAC.
# The handler receives data.shop == "victim-shop.myshopify.com" despite the request
# never having been sent by or for that shop.
```

### Citations

**File:** docs/usage/webhooks.md (L14-14)
```markdown
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L26-26)
```markdown
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
