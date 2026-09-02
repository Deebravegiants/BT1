### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook request by validating an HMAC that covers only the raw request body, then dispatches to the app's handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers. This breaks the equality "shop the HMAC authenticates == shop the handler acts on," allowing a shop-domain/topic swap on an otherwise validly-signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC over that signable string (the body only) and, once it passes, trusts `request.topic` to select the handler and `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever verifies `verifiable_query.to_signable_string` against `verifiable_query.hmac`; for a webhook `Request` that string is the body, so the identity/tenant fields conveyed via headers are not part of what is verified: [4](#0-3) 

The equality that should hold is: `shop authenticated by HMAC == shop used to build WebhookMetadata.shop`. Because the HMAC signable string never includes the shop-domain (or topic) header, this equality is not enforced by the library — any request bearing a body+HMAC pair that is valid for the configured `api_secret_key` will be accepted regardless of which `x-shopify-shop-domain` / `x-shopify-topic` header values accompany it. The documentation explicitly tells integrators that `process` "will verify the request did indeed come from Shopify," implying that all fields on `WebhookMetadata` (including `shop`) are safe to trust for tenant identification: [5](#0-4) 

### Impact Explanation
An unprivileged internet user who is themselves a legitimate merchant (or otherwise controls a Shopify shop that has the app installed) legitimately receives real webhook deliveries — genuine `raw_body` + valid `hmac` pairs signed with the app's `api_secret_key` — for their own shop. Because the header fields are excluded from the signature, that same attacker can resend the identical raw body and HMAC to the app's shared webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) with a victim shop's domain or a different registered topic. `Utils::HmacValidator.validate` still returns `true` (the body/secret pair is genuinely valid), so `Registry.process` proceeds to invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain and attacker-controlled body content. Any handler that uses `data.shop` to key off session/store lookups (as the documented example pattern does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process the attacker's forged/self-authored data as if it originated from the victim shop — a tenant-identity confusion / cross-tenant data-injection primitive.

### Likelihood Explanation
Exploitation requires only that an attacker be able to run/own a shop with the vulnerable app installed (a normal, unprivileged relationship any merchant can obtain) so they can capture one legitimate `raw_body + hmac` pair for a controllable topic, then replay it to the shared webhook endpoint with a swapped `shop-domain`/`topic` header. No access token, `client_secret`, or elevated permission is required, and the webhook endpoint is typically public/unauthenticated by design.

### Recommendation
Bind the tenant/topic identity into the signed material, or otherwise cryptographically tie header values to the payload before trusting them: e.g., include `topic` and `shop-domain` in the value verified by `HmacValidator` (mirroring `AuthQuery#to_signable_string`, which does include `shop`), or require the caller to independently verify shop/topic against the webhook subscription that Shopify's API confirms was registered for that specific shop before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and enables an `orders/create` webhook they control content for (e.g., by placing a test order with attacker-chosen order fields).
2. Attacker's endpoint (or a captured HTTP log/proxy they control) records the genuine `raw_body` and the `x-shopify-hmac-sha256` value Shopify sent for that delivery.
3. Attacker re-sends an HTTP POST to the app's shared webhook route with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (a shop they don't own):
```ruby
request = ShopifyAPI::Webhooks::Request.new(
  raw_body: captured_raw_body,
  headers: {
    "x-shopify-topic" => "orders/create",
    "x-shopify-hmac-sha256" => captured_hmac,
    "x-shopify-shop-domain" => "victim-shop.myshopify.com",
  },
)
ShopifyAPI::Webhooks::Registry.process(request)
```
4. `Utils::HmacValidator.validate(request)` passes because it only checks `raw_body` against the secret, and the handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and attacker-controlled body — confirming the shop bound to the accepted webhook is not the shop actually authenticated by the signature.

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
