### Title
Webhook HMAC does not bind the `shop`, `topic`, or `webhook_id` identity fields, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification. The `shop`, `topic`, `webhook_id`, and `api_version` values — all of which are trusted and forwarded to the app's webhook handler as tenant-identifying data — come from unauthenticated HTTP headers that are never included in the signed payload. This breaks the identity binding `HMAC(secret, signed_bytes) == received_hmac` from also authenticating `shop`, letting anyone who can produce one valid `(raw_body, hmac)` pair for the app (e.g. as a legitimate merchant of the app) replay it with an arbitrary `shop-domain` header to impersonate a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no cryptographic protection: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received value: [4](#0-3) 

Because `to_signable_string` for webhooks is exactly `@raw_body`, the signature is invariant with respect to the `shop-domain`, `topic`, and `webhook-id` headers. Two requests with identical bodies but different `shop-domain` headers produce the same valid HMAC. The documented processing flow explicitly instructs apps to trust `data.shop` from the resulting `WebhookMetadata` for tenant routing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [5](#0-4) [6](#0-5) 

This is the same bug class as the report: an identity-relevant field (`shop`) is acted upon by downstream logic without being covered by the authentication check (the HMAC), so the check answers permissively regardless of that field's value.

### Impact Explanation
An unprivileged internet user who runs their own shop with the target app installed will legitimately receive real webhook deliveries: a body and a valid HMAC signed with the app's shared secret, plus headers identifying their own shop. Because the HMAC does not bind `shop`/`topic`/`webhook_id`, that same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `shop-domain` header (and/or `topic`, `webhook-id`) changed to a victim shop's domain. `Registry.process` will accept it as authentic and dispatch it to the handler as if it originated from the victim tenant, since it only re-validates the HMAC over the (unchanged) body. This is a cross-tenant data-integrity/confusion issue: an app that persists or acts on webhook data keyed by `data.shop` (as recommended in the gem's own docs) can have its per-tenant state corrupted or misattributed by an attacker who only needs to control their own installation, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is moderate-to-high in realistic app deployments: capturing your own webhook traffic (body + `X-Shopify-Hmac-Sha256` + other headers) requires no special access beyond installing the app on a shop the attacker controls, which is the normal "unprivileged internet user" position for a public app. Replaying the POST to the app's public webhook endpoint with a modified `shop-domain` header requires only basic HTTP tooling. The main constraint is that the replayed body must remain byte-identical to what was originally signed (so the attack works best for topics/bodies that don't strictly need to differ from the captured payload, or where the attacker controls the content of their own shop's data, e.g. `products/update`, `orders/create` webhooks whose bodies they can influence by acting on their own store).

### Recommendation
Include the identity-relevant header values (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material used to validate the webhook, or otherwise cryptographically bind them to the signature (e.g., verify them against Shopify's out-of-band webhook subscription metadata, or require the host app to cross-check `data.shop` against a known/installed shop list before trusting it). At minimum, update `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` so that the HMAC check fails if these header values are altered relative to what Shopify actually sent for that event, and document that `data.shop` alone must not be treated as fully authenticated tenant identity without an out-of-band cross-check.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers, e.g., `products/update` webhooks.
2. Shopify sends a legitimate webhook to the app: raw body `B`, headers `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: products/update`.
3. Attacker captures `(B, H)` (they receive it directly, or it appears in logs/network they control) and crafts their own product data so that `B` contains attacker-chosen JSON.
4. Attacker POSTs to the app's public webhook endpoint reusing the exact same body `B` and `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `HmacValidator.validate` recomputes `HMAC(secret, B)`, which still equals `H`, so validation succeeds. [7](#0-6) 
6. `Registry.process` invokes the handler with `WebhookMetadata` where `shop == "victim-shop.myshopify.com"` but `body` is fully attacker-controlled content, causing the host app to act on/store attacker data under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L19-29)
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
