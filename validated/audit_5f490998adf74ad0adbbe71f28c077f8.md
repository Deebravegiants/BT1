### Title
Webhook shop/topic identity spoofing via HMAC that only covers the body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature exclusively from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` only checks that the body's HMAC is valid, then passes the header-derived `shop` value straight to the app's handler as trusted tenant identity. Because the shop identity is a field acted on but not covered by the HMAC, an attacker who can obtain one valid `(raw_body, hmac)` pair (trivially, by installing the app on their own shop and receiving a legitimate webhook) can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop, and the gem will accept it as authentic.

### Finding Description
The identity binding that should hold is: `hmac_is_valid_for(raw_body) == shop_header_is_authentic`. In this gem, the HMAC only authenticates `raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are parsed from headers that are never included in the signable string: [2](#0-1) 

`Registry.process` validates only the body HMAC and then forwards the unauthenticated `request.shop` (and other header-derived fields) directly to the app-supplied handler as `WebhookMetadata`: [3](#0-2) 

`HmacValidator.validate` confirms it only ever checks `verifiable_query.hmac` against `to_signable_string`, with no binding to the shop header: [4](#0-3) 

The gem's own documentation states that calling `Registry.process` "will verify the request did indeed come from Shopify," implying full authenticity verification, when in fact only the body is authenticated and the shop identity is not bound to the signature: [5](#0-4) 

An attacker who has any legitimate app installation (e.g., on their own development store) can capture one valid `(raw_body, X-Shopify-Hmac-Sha256)` pair from Shopify, then POST that identical body/HMAC to the app's webhook endpoint while changing `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) to point at a different, victim shop. `Utils::HmacValidator.validate` still returns true (it only checks the body), so `Registry.process` dispatches to the handler with `shop` set to the attacker-chosen victim domain.

### Impact Explanation
Any host application that uses `data.shop` from `WebhookMetadata` to key writes, session lookups, or business logic per tenant (exactly as the gem's own documented example does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to process attacker-supplied webhook bodies under a victim shop's identity. This is a cross-tenant identity confusion: the gem asserts "this webhook is verified to be for shop X" when it has only verified "this body was HMAC-signed by our shared secret" — the two are not the same guarantee, since the secret is shared by all shops installing the app, and the shop-binding half of that guarantee is silently missing.

### Likelihood Explanation
Exploitation requires the attacker to have their own valid install (already assumed as attacker capability — creating a dev/free shop and installing the app costs nothing and gives them a stream of correctly-HMAC'd webhook bodies for arbitrary topics they can trigger themselves, e.g. `products/update` on their own store). No secret, access token, or privileged account belonging to the victim is needed — only unauthenticated HTTP access to the app's public webhook endpoint. The trigger requires waiting for/generating a webhook and then replaying it with a different domain header, which is straightforward.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) into the value that is HMAC-verified, or otherwise cryptographically tie the shop domain to the signed payload before trusting it in `WebhookMetadata`. At minimum, document prominently that `shop` in `WebhookMetadata` is not authenticated by the HMAC and must be independently cross-checked by the host application against a known/expected shop before being used for tenant-scoped operations.

### Proof of Concept
```ruby
# Attacker has a legitimate install on their own shop "attacker.myshopify.com"
# and receives (or triggers) a real webhook, capturing:
raw_body = '{"id":1,"note":"hello"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
) # this is a real signature the attacker legitimately received from Shopify

# Attacker now POSTs the same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to target a victim shop they do not control:
headers = {
  "x-shopify-topic" => "products/update",
  "x-shopify-hmac-sha256" => valid_hmac,      # still valid, since body is unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled value
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate passes (only checks raw_body),
#    handler.handle is invoked with data.shop == "victim-shop.myshopify.com"
```

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
