This confirms the identity binding gap: `Registry.process` dispatches `WebhookMetadata` (including `shop: request.shop`) to the app's handler after only validating `Utils::HmacValidator.validate(request)`, which in turn calls `request.to_signable_string` — and `Request#to_signable_string` returns only `@raw_body`, never the `shop-domain` header.### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then hands the app's handler a `WebhookMetadata` struct whose `shop` field is populated straight from an unauthenticated HTTP header. The signature never covers that header, so the "shop" identity the host application uses to tenant-scope the webhook is not bound to the bytes that were actually verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that signable string: [2](#0-1) 

Meanwhile `Request#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in `to_signable_string` and therefore plays no role in the HMAC check: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards `request.shop` unchanged into `WebhookMetadata`, which is delivered to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The identity-binding equality that should hold is:
`shop bound by HMAC == shop delivered to handler`
but in this implementation:
`shop bound by HMAC (∅, not signed) != shop delivered to handler (attacker-controllable header)`.

Any party capable of obtaining one valid `(raw_body, hmac)` pair from Shopify — e.g., a developer/tester who owns their own shop and receives legitimate webhooks for it — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. Because the HMAC only certifies "this body came from Shopify," not "this body belongs to shop X," the request still passes `HmacValidator.validate`, and the handler receives `WebhookMetadata#shop` set to the attacker-chosen domain instead of the shop that actually generated the payload.

### Impact Explanation
Shopify app implementations commonly use `WebhookMetadata#shop` as the tenant key to look up the merchant's stored session/access token, update per-shop database records, or route the webhook body into shop-scoped storage — this is exactly the intended usage documented for `Registry.process`: [6](#0-5) 

Since the gem provides no cross-check between the authenticated body and the claimed shop, an attacker can cause the host application to process/attribute webhook data (order info, GDPR events, uninstall notices, etc.) under an arbitrary victim shop domain of their choosing. Depending on how the host app uses the `shop` value (e.g., to key access to the target merchant's data or trigger the target merchant's fulfillment/uninstall flow), this crosses the tenant boundary the gem is expected to enforce, satisfying the High-severity criterion for a broken identity binding.

### Likelihood Explanation
The attacker only needs the ability to receive one genuine webhook for any shop (trivially available to anyone who installs the app on their own development store) and the ability to send an arbitrary HTTP POST with custom headers to the app's public webhook endpoint — no `api_secret_key`, access token, or privileged account is required. This is directly reachable through the gem's documented `Registry.process` API.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind the reported `shop` to the verified body before constructing `WebhookMetadata`, so a replayed/relabeled body cannot be attributed to a different shop.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and its `x-shopify-hmac-sha256` header — a valid `(raw_body, hmac)` pair signed with the app's real secret.
2. Attacker POSTs the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header without complaint (`lib/shopify_api/webhooks/request.rb:45-63`), and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. The app's handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-supplied data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L123-136)
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
```
