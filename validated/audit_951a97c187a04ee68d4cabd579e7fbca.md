### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, while `ShopifyAPI::Webhooks::Registry.process` extracts the tenant identity from a separate, unsigned header (`shop-domain`) and passes it straight to the host app's handler as the trusted tenant key. An attacker who can obtain one valid `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own shop and capturing/replaying its webhooks) can resend that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. HMAC validation still passes because the shop is never part of the signed material, so the host app processes attacker-controlled data under a victim shop's identity.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which only returns `@raw_body`. `Utils::HmacValidator.validate` computes and compares the HMAC solely over this signable string: [2](#0-1) 

Meanwhile, `Request#shop` is read from the unsigned `shop-domain` header: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then forwards the header-derived `request.shop` (along with `topic`, `webhook_id`, `api_version`) directly into `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle`: [4](#0-3) [5](#0-4) 

The identity binding broken here is: `shop` acted upon (used by the host app to key per-tenant data/session lookups) ≠ `shop` covered by the HMAC (only `raw_body` is signed). Because the app's `client_secret`/`api_secret_key` is shared across all shops using the app, any tenant that has legitimately installed the app can generate a validly-signed body. That attacker-controlled `(raw_body, hmac)` pair remains valid for *any* shop domain value, since the shop is never mixed into the signature computation. Docs confirm the documented processing flow relies on `Registry.process` for both authenticity and topic dispatch: [6](#0-5) 

### Impact Explanation
This breaks the tenant boundary this gem is responsible for enforcing on behalf of the host app: `Registry.process` is the sole authenticity gate host apps rely on before trusting `WebhookMetadata#shop` as the source-of-truth tenant identifier. A malicious merchant/tenant of a multi-tenant Shopify app can forge webhook deliveries "as" a different shop (e.g. to inject data, trigger redact/GDPR flows, or corrupt per-shop state keyed by `shop`), constituting cross-tenant access facilitated entirely by this gem's webhook-verification contract.

### Likelihood Explanation
Any user who can install the target app on a shop they control can capture one legitimate webhook `(raw_body, x-shopify-hmac-sha256)` pair for a topic of interest (many topics, e.g. `app/uninstalled`, have static or attacker-influenced bodies), then replay it directly to the app's public webhook HTTP endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop. No secrets, tokens, or privileged access are required beyond running the app once as an ordinary merchant.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the material that is HMAC-verified, or otherwise cryptographically bind them to the signed body, so that `to_signable_string` cannot be satisfied by a payload signed for a different shop.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic and capture the raw POST body `B` and header `x-shopify-hmac-sha256: H`.
2. Send a new HTTP request to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H`, so `Registry.process` treats the request as authentic and calls the host handler with `WebhookMetadata(shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, even though the body/topic actually originated from the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
