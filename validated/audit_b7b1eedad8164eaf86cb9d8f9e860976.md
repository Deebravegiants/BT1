## Analysis

The Cubist bug is a case where a request is processed using the wrong identity context because a critical field is trusted without being covered by the same authentication mechanism that "proves" the request is legitimate. The same pattern exists in this gem's webhook processing.

### The identity binding that should hold

`shop header the handler dispatches on == shop bytes covered by the webhook HMAC`

### Where it breaks

`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body — it does **not** include the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the signature purely over `to_signable_string`: [2](#0-1) 

`Webhooks::Registry.process` gates on that HMAC check and then dispatches using `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` — all read straight from the (unsigned) headers: [3](#0-2) 

The gem's own docs describe `Registry.process` as verifying "the request did indeed come from Shopify," implying the whole payload (including which shop it's from) is authenticated, but only the body bytes are actually covered: [4](#0-3) 

### Exploitability

Any internet user can freely create a Shopify development store and install a public app that uses this gem (or trigger any webhook-generating action on a store they control). Shopify signs that webhook body with the app's shared secret exactly as it would for any other merchant — this doesn't require stealing `api_secret_key`, an access token, or TLS interception. The attacker then has a `(raw_body, valid_hmac)` pair. Because the headers are outside the signed content, the attacker can replay that exact body+HMAC to the app's public webhook endpoint while forging `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) to name a **victim** shop. `HmacValidator.validate` still returns `true` because the body is unmodified, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: <forged victim shop>, body: <attacker-controlled body>, ...)`.

### Title
Webhook shop/topic/id headers are trusted for tenant attribution without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers. `Webhooks::Registry.process` nonetheless uses these unauthenticated headers to attribute the incoming webhook to a specific tenant/shop before invoking the app's handler.

### Finding Description
`HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb#L12-31) computes the HMAC over `verifiable_query.to_signable_string`. For webhook requests, that method returns only `@raw_body` (lib/shopify_api/webhooks/request.rb#L36-38) — none of the Shopify-supplied identification headers are part of the signed content. `Registry.process` (lib/shopify_api/webhooks/registry.rb#L188-199) treats a passing HMAC check as proof the entire request — including `request.shop`, `request.topic`, and `request.webhook_id` read from headers — is authentic, and forwards those unauthenticated values straight to the app's `WebhookHandler`. Any party able to obtain one legitimately-signed webhook body (trivial: install the app on a store they control) can resend that exact body with a forged `shop-domain` header naming a different shop, and the forged tenant identity will pass validation and reach the handler.

### Impact Explanation
This crosses a tenant boundary: the host application will process attacker-supplied webhook content as though it originated from a shop the attacker does not control (`data.shop` used by handlers, per docs/usage/webhooks.md#L12-17, to route/store data per-tenant). This matches the Critical bucket for cross-tenant access — a shop's webhook-derived state can be polluted with data attributed to it that never actually came from that shop's events.

### Likelihood Explanation
Requires no privileged credentials, no `api_secret_key`, no token theft, and no TLS interception — only the ability to create a store/install the target app (open to any internet user) to obtain one valid `(body, hmac)` pair, then a single forged HTTP request to the app's public webhook endpoint.

### Recommendation
Include the header values the application relies on for tenant/topic attribution (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable content, or otherwise cryptographically bind them (e.g., validate `shop-domain` against a shop that has confirmed installation/session state) before dispatching to the handler, rather than trusting them solely because the body's HMAC validated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (or triggers any subscribed webhook topic) and captures a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(app_secret, B)`).
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`.
3. `Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds `request.shop == "victim-shop.myshopify.com"`.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process/store attacker-chosen content under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
