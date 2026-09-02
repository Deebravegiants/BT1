I have sufficient evidence to confirm this finding. The root cause is fully supported: `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) verifies a signature only against `verifiable_query.to_signable_string`, and `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) returns only `@raw_body` — never the `shop`, `topic`, or `webhook_id` headers that `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) hands to the app's handler as the trusted tenant identity.

### Title
Webhook shop/topic/webhook_id identity is not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by calling `Utils::HmacValidator.validate(request)`, which computes the HMAC only over `request.to_signable_string`, i.e. the raw request body [1](#0-0) [2](#0-1) . The `shop`, `topic`, and `webhook_id` values that are forwarded to the app's handler as the authenticated event identity are read straight from unauthenticated HTTP headers and are never part of the signed bytes [3](#0-2) .

### Finding Description
The broken equality is:
`bytes covered by HMAC` (`@raw_body` only) ≠ `identity fields acted on by the handler` (`shop`, `topic`, `webhook_id` headers).

`Registry.process` does:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [4](#0-3) 

`Utils::HmacValidator.validate` only proves that the given `raw_body` was signed by Shopify's secret at some point; it says nothing about which shop, topic, or webhook id that signature was originally issued for, since `Request#to_signable_string` never includes them [5](#0-4) .

The gem's own documentation explicitly promises this call "will verify the request did indeed come from Shopify" for the webhook as a whole, and shows the host app trusting `data.shop` as the tenant key (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so an app author following the documented API as shown is still exposed [6](#0-5) [7](#0-6) .

### Impact Explanation
An unprivileged internet user who controls (or installs the app on) any shop — including a free Shopify partner/dev store — can capture a legitimate `(raw_body, hmac)` pair from a webhook Shopify sends for their own shop (e.g. `orders/create`), then replay that exact body and HMAC to the target app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it only checks the unmodified body, and `Registry.process` forwards the attacker-chosen shop/topic to the handler as if Shopify itself asserted that identity. This is cross-tenant event/data injection into whatever the host app does with `data.shop` and `data.body` (e.g. writing order/product data under another merchant's tenant record), which maps to the Critical "cross-tenant access" category.

### Likelihood Explanation
The attack requires no access to `api_secret_key`, access tokens, or the victim's credentials — only a shop the attacker controls (trivially obtainable via a free Shopify dev/partner store) and the ability to POST arbitrary headers to the app's public webhook callback URL, which is by definition internet-reachable. The library provides no mitigation; it is architecturally intrinsic to `Request#to_signable_string` and `HmacValidator.validate`.

### Recommendation
Include the shop domain, topic, and webhook id (or at minimum the shop domain) in the HMAC-signable payload used by `Webhooks::Request`, or otherwise cryptographically bind them to the verified body before they are exposed to `Registry.process`/`WebhookMetadata`, so that a validly-signed body for shop A cannot be replayed and re-attributed to shop B.

### Proof of Concept
```ruby
# Attacker owns shop "attacker-shop.myshopify.com" and receives a real Shopify webhook:
raw_body = '{"id":1,"note":"legit order"}'
hmac_b64 = "<value Shopify actually sent for attacker-shop's webhook>"

# Attacker replays it against the target app's webhook endpoint, but swaps the shop header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,          # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
