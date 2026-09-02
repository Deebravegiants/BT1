### Title
Webhook `shop` Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the HMAC it checks only covers the raw request body. The `shop` attribute that handlers use to identify which merchant tenant the webhook belongs to comes from an unauthenticated HTTP header and is never included in the signed material, so it can be swapped without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the body or signature: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the body bytes only: [3](#0-2) 

`Registry.process` raises only if that body-only HMAC fails, then immediately trusts `request.shop` and hands it to the app's handler as the tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`hmac_valid(body, secret) == true` should imply `shop_header == shop_that_actually_generated(body)`.

In this implementation that equality does not hold: `hmac_valid(body, secret)` only proves the body bytes weren't tampered with under the app's shared secret — it says nothing about which shop's header accompanies it. Since one `api_secret_key`/`client_secret` is shared across every shop that has the app installed, any merchant that receives legitimate webhook deliveries for their own shop can capture a valid `(body, hmac)` pair and replay it with a different `shop-domain` header value. The signature still validates because the header is outside the signed content.

The library's own webhook documentation confirms this is meant to be a trust boundary ("This will verify the request did indeed come from Shopify") and its own example handler uses `data.shop` directly to route/attribute the event to a tenant record: [5](#0-4) [6](#0-5) 

### Impact Explanation
Any app built on top of this gem that uses `WebhookMetadata#shop` (as the gem's own documented example does) to select which merchant's data to create/update/act upon is exposed to cross-tenant webhook forgery: a malicious or compromised merchant with a legitimate app installation can attribute forged/replayed webhook events to a different merchant's shop, since the gem provides no binding between the verified body and the claimed shop identity. This falls under the Critical "cross-tenant access" category, because the security boundary the library is supposed to enforce (per-shop authenticity of webhook events) is not actually enforced for the `shop` field.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the app on at least one shop (a normal, unprivileged merchant capability) and capture one of their own valid webhook deliveries, then replay it with a modified `shop-domain` header to the app's webhook endpoint. No access token, `client_secret`, or privileged credential is required — the attacker only needs their own legitimate webhook traffic, which they naturally receive.

### Recommendation
Include the shop domain (and topic) inside the HMAC-signed material, or otherwise cryptographically bind `request.shop` to the verified body (e.g., derive/confirm the shop from a signed claim rather than an unauthenticated header) before it is passed to `WebhookMetadata` and handler code. At minimum, update documentation to make explicit that `data.shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification (e.g., cross-checking against the shop associated with the specific webhook subscription/topic combination server-side).

### Proof of Concept
1. Install the app on `attacker.myshopify.com` and let Shopify deliver a legitimate webhook, e.g. `orders/create`, to the app's callback endpoint. Capture the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the shared `api_secret_key`).
2. Craft a new POST to the same webhook endpoint with the identical body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `HmacValidator.validate` succeeds because it only checks `H` against `B` (see `to_signable_string`), independent of the shop header.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)`, and any handler logic keyed off `data.shop` (as shown in the gem's own documented example) now acts on the victim's tenant using attacker-controlled body content.

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

**File:** docs/usage/webhooks.md (L19-30)
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
