This confirms the finding. The docs at `docs/usage/webhooks.md:125` explicitly state that `Registry.process` "will verify the request did indeed come from Shopify" — implying the entire request (including shop identity) is authenticated by this call — but the HMAC verification only covers the raw body, not the `shop-domain` header that the handler is given as the trusted `data.shop` value.

### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then passes `request.shop` (read from an HTTP header) to the app's webhook handler as the trusted tenant identifier. However, the HMAC only signs the raw request body — the `shop-domain` header is never included in the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop` as the tenant identity handed to the handler: [3](#0-2) 

The identity binding that should hold is: `shop reported to handler == shop that the HMAC secret was computed for`. Because the app's `api_secret_key` is shared across every shop that installs the app, and `shop-domain` is not part of the signed content, any request bearing a *valid (body, hmac)* pair — e.g. one an attacker legitimately received from their own installed test store, or a captured legitimate webhook body they can replay — can be POSTed directly to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` header naming a different, victim shop. The HMAC check passes (it only verifies the body wasn't tampered with), so `Registry.process` calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` claiming to be the victim's shop.

The library's own documentation reinforces the false sense of security: `docs/usage/webhooks.md` says `process` "will verify the request did indeed come from Shopify," which a reasonable integrator reads as covering the reported shop, not just body integrity. [4](#0-3) 

### Impact Explanation
Any host application that uses `data.shop` (as documented) to select the tenant record to update — the officially demonstrated pattern in `docs/usage/webhooks.md` (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`) — can be made to attribute attacker-supplied payloads to a different merchant's shop. This is a cross-tenant data-injection primitive: an attacker who is a legitimate (if unprivileged) user of the app on their own store can forge webhook events "from" any other installed shop, since the same `api_secret_key` validates the HMAC for all shops of that app.

### Likelihood Explanation
Likelihood is high for any deployment following the gem's documented handler pattern (`data.shop` used as tenant key) without additional out-of-band verification, since the attacker only needs one legitimate `(raw_body, hmac)` pair from any shop where the app is installed (trivially obtained by installing the app on their own store and capturing a real webhook) and the ability to POST to the webhook endpoint URL, which is by design public/unauthenticated prior to HMAC check.

### Recommendation
Bind the shop identity to the signed content, or require the caller to supply an independently trusted shop context. Concretely, either:
- Add the `shop-domain`, `topic`, and `webhook-id` headers into the signable string used for HMAC computation (this would require Shopify to change what it signs, so is not solely fixable client-side), or
- Document and/or enforce in `Registry.process` that the reported `shop` must be checked by the caller against a shop that has an active, stored session/access token before trusting `data.shop`, and update `docs/usage/webhooks.md` to make this an explicit, mandatory step rather than implying `process` fully "verifies the request came from Shopify."

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and captures a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because it's HMAC-SHA256(`B`, shared `api_secret_key`)).
2. Attacker POSTs to the app's public webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts it (only checks for header presence), `Utils::HmacValidator.validate` succeeds because it recomputes HMAC over `B` only: [5](#0-4) 
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the host app (following the documented pattern) processes/enqueues work attributed to `victim.myshopify.com` using attacker-controlled body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
