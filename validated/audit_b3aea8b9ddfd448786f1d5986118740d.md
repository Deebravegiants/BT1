### Title
Webhook HMAC only authenticates the request body, not the `shop-domain` / `topic` headers, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking an app's webhook handler with the shop identity attached to that request [1](#0-0) . In reality, the HMAC signature that the gem validates only covers the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — which are passed straight through to the handler as trusted identity data — come from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers with no cryptographic binding to that body: [3](#0-2) [4](#0-3) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., the body only) and compares it with the received `hmac-sha256` header using a constant-time comparison: [5](#0-4) 

`Registry.process` treats a passing HMAC check as full authentication of the whole request, then forwards the unauthenticated `shop` header value straight into `WebhookMetadata` given to the app's handler: [6](#0-5) 

The identity binding that should hold is:
`shop value cryptographically bound to the signed payload == shop value the handler treats as the webhook's origin`

That equality does not hold: the `shop-domain`, `topic`, `webhook_id`, and `api_version` headers can be modified in transit or replayed with a different value than what was actually signed for, without invalidating the HMAC, because they are never part of the signed material. Anyone who can obtain one validly-signed `(body, hmac)` pair — for example, from their own shop's legitimately triggered webhook deliveries, since request bodies for many topics are attacker-controllable/predictable (they own that shop's data) — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header naming a different, victim shop, and/or substituting the `x-shopify-topic` header to route to a different handler than the one Shopify actually fired. `Registry.process` will accept it as authentic (HMAC still matches, since only the body is checked) and will hand the handler `WebhookMetadata` claiming that data came from the victim shop and/or from a different topic than actually occurred.

### Impact Explanation
This breaks the shop/tenant identity binding for webhook-driven app logic: an app that keys persisted data, GDPR redaction handling, billing/entitlement changes, or other side effects off `WebhookMetadata#shop` and `#topic` can be made to perform operations attributed to another merchant's shop, using content the attacker fully controls. This is a cross-tenant identity-boundary violation: the handler is invoked believing it received data for shop B when in fact the signed bytes only ever proved they came (unmodified) from Shopify for some request — not that they concern shop B or a given topic.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one validly-signed `(body, hmac)` pair, which any merchant that has installed the app can obtain by observing/predicting the webhook bodies delivered for their own store (bodies are often deterministic templates per topic, e.g., GDPR/mandatory webhooks or simple resource events). No access to `api_secret_key`, access tokens, or privileged accounts is required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers and a previously-observed signed body, which is squarely within scope of an "unprivileged internet user."

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signed/verified material, or otherwise cryptographically bind them to the payload before trusting them in `WebhookMetadata`, so that `Utils::HmacValidator.validate` authenticates the full identity tuple rather than the body alone.

### Proof of Concept
1. Install the target app on an attacker-owned shop (`attacker.myshopify.com`) and trigger a webhook delivery for a topic whose body is predictable/attacker-controlled (e.g., `orders/create` with attacker-chosen order fields, or a mandatory GDPR topic body).
2. Capture the resulting `raw_body` and its correct `x-shopify-hmac-sha256` value as delivered to the app's webhook endpoint (the HMAC is `HMAC-SHA256(api_secret_key, raw_body)` per `lib/shopify_api/utils/hmac_validator.rb`).
3. Replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint, but set:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: <topic mapped to a sensitive handler>`
4. `ShopifyAPI::Webhooks::Registry.process` recomputes the HMAC over `raw_body` only, finds it valid, and invokes the registered handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: <attacker-chosen>, body: <attacker-controlled>)`, even though Shopify never sent this event for that shop or topic.

### Citations

**File:** docs/usage/webhooks.md (L123-135)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

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

**File:** lib/shopify_api/webhooks/request.rb (L15-15)
```ruby
      sig { returns(String) }
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
