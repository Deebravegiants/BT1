Docs explicitly claim `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and the handler is told that `data.shop` is "The shop domain of the webhook" [2](#0-1) , i.e., an authenticated attribute of the verified request. This matches the report's bug class of "a field acted on but not covered by the HMAC."

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) attribution is not covered by the HMAC, allowing cross-tenant webhook spoofing/replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw body, then dispatches the handler using the `shop` (and `topic`, `webhook_id`, `api_version`) values taken from unauthenticated HTTP headers.

### Finding Description
`Registry.process` calls `Utils::HmacValidator.validate(request)` and, if it passes, builds `WebhookMetadata` from `request.shop`, `request.topic`, etc., before calling the app's handler [3](#0-2) .

`HmacValidator.validate` signs/verifies using `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method is defined to return only `@raw_body` [4](#0-3) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors instead read directly from HTTP headers with no cryptographic binding to the HMAC at all [5](#0-4) .

The identity-binding equality the gem implicitly claims to enforce is:
`HMAC-verified-bytes == (raw_body, shop, topic, webhook_id, api_version)`

but the actual equality enforced is only:
`HMAC-verified-bytes == raw_body`

`shop` is a header value that is never included in `compute_signature`'s input (`OpenSSL::HMAC.hexdigest(..., verifiable_query.to_signable_string)`) [6](#0-5) . Consequently, any request whose body+HMAC pair is valid for the app's secret will be accepted regardless of what `shop-domain`/`x-shopify-shop-domain` header accompanies it, letting an unprivileged attacker in control of the header value make the gem attribute the (otherwise correctly signed) payload to an arbitrary shop.

### Impact Explanation
Because `data.shop` is documented and treated as the authenticated tenant identifier for the webhook ("The shop domain of the webhook") [2](#0-1) , and `Registry.process` is documented as verifying "the request did indeed come from Shopify" [1](#0-0) , host applications reasonably rely on `data.shop` to key session/data lookups (as the gem's own doc example does: `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [7](#0-6) ). An attacker who obtains one valid `(raw_body, hmac)` pair (e.g., from a webhook delivered to their own shop, or a captured/replayed request) can resend it to the app's webhook endpoint with a different `shop-domain` header, causing the app to process/store that payload under a victim shop's tenant context — a cross-tenant confusion enabled purely because the identity-binding field (`shop`) is not covered by the HMAC that the gem itself computes and validates.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and one previously-observed valid `(body, hmac)` pair — no access to `api_secret_key`, tokens, or any privileged credential is needed, satisfying the "unprivileged internet user" threat model. The endpoint is a public HTTP callback by design (registered during OAuth), so it is reachable by any internet user who can send an HTTP POST.

### Recommendation
Include the identity-binding headers (`shop`, `topic`, `webhook_id`, `api_version`) in the material verified against the HMAC, or otherwise cryptographically/logically bind them to the signed body (e.g., re-deriving the expected shop from a server-side webhook-id lookup keyed off Shopify's registration, or requiring these values be included in the signed payload) before constructing `WebhookMetadata` and dispatching to the handler in `Registry.process` [8](#0-7) .

### Proof of Concept
1. App registers webhook handler for `orders/create` and calls `Registry.process` on every inbound POST to its webhook route, per the documented pattern [9](#0-8) .
2. Attacker (an unprivileged internet user, potentially the operator of their own installed shop `attacker.myshopify.com`) captures a legitimately delivered webhook: `raw_body = '{"id":1,...}'` with header `x-shopify-hmac-sha256` computed by Shopify over that body using the app's real secret, and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` recomputes the HMAC only over `raw_body` [4](#0-3)  and it matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` [10](#0-9) , causing the host app to treat attacker-controlled data as belonging to `victim.myshopify.com`.

### Citations

**File:** docs/usage/webhooks.md (L14-14)
```markdown
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** docs/usage/webhooks.md (L128-135)
```markdown
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
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
