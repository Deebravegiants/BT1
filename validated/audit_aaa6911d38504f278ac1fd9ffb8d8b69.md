### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely by checking the HMAC over the raw request body, then trusts the unrelated, unauthenticated `x-shopify-shop-domain` header as the tenant identifier passed to the app's handler. Because the shop field is never included in the signed material, any bytes that carry a valid `(raw_body, hmac)` pair can be replayed with an arbitrary `shop` header value and will be accepted and dispatched as if it belonged to that different shop.

### Finding Description
`HmacValidator.validate` computes the expected signature only from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns just the raw HTTP body — none of the Shopify headers are included in the signable content: [2](#0-1) 

The `shop` accessor, however, is read straight from the `x-shopify-shop-domain` header, which is completely outside the HMAC's coverage: [3](#0-2) 

`Registry.process` only asserts `Utils::HmacValidator.validate(request)` (i.e., "was this body signed with our secret") and then immediately forwards `request.shop` to the handler as the trusted tenant identifier, with no additional binding between the verified bytes and the claimed shop: [4](#0-3) 

This breaks the identity binding that `process` implicitly claims to provide. Per the library's own docs, `process` is described as verifying "the request did indeed come from Shopify" before invoking the handler for "a specific shop": [5](#0-4) 

but the equality that actually matters for multi-tenant correctness — `shop_claimed_in_header == shop_the_signed_bytes_originated_from` — is never checked. Only `hmac(body) == received_hmac` is checked; `shop` is disjoint from `body` in the signable string, so the check validates "these bytes came from an app installation using our secret" but not "these bytes are about shop X."

### Impact Explanation
Any party who can obtain one legitimate `(raw_body, hmac)` pair signed with the app's secret — trivially achievable by installing the app on their own store and capturing one of their own real webhook deliveries — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value. `HmacValidator.validate` still returns `true` (the body-derived HMAC is untouched), and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain. Any handler logic that uses `shop` to scope tenant data (e.g., updating settings, marking installation state, writing to a shop-keyed record) can be made to act on/against a shop the attacker does not own — a cross-tenant confusion/access primitive delivered through a request that superficially "passed HMAC verification."

### Likelihood Explanation
Webhook endpoints are, by the documented integration pattern, public unauthenticated routes that only rely on `Registry.process`'s HMAC check for trust: [6](#0-5) 

Obtaining one valid `(body, hmac)` sample requires nothing more than installing the target app on an attacker-controlled development store (a normal, unprivileged action), after which the header can be freely rewritten and replayed indefinitely (the same body/HMAC pair is valid forever since it isn't time-bound and isn't shop-bound). No secret, token, or privileged access is required.

### Recommendation
Cross-check the header-derived `shop` value (and ideally `topic`/`webhook_id`) against expectations before trusting it — e.g., require the caller to supply the expected shop for the delivery being processed and compare it (constant-time) against `request.shop`, or bind shop/topic/webhook-id into the signable string used for HMAC verification instead of relying on unauthenticated headers.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker-shop.myshopify.com`; trigger any webhook topic (e.g. `app/uninstalled`) to capture a real delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `HMAC(secret, B) == H`).
2. POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and finds it equals `H` — validation passes (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), and the app's handler executes tenant-scoped logic believing this event genuinely originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```

**File:** docs/usage/webhooks.md (L127-136)
```markdown
```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
