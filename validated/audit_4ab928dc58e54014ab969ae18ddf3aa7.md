Confirmed: `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` returns only `@raw_body`, so the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never part of the HMAC-signed content, yet `Registry.process` uses `request.shop` (and `request.topic`) to route/attribute the webhook to a tenant.

### Title
Webhook tenant identifier (`shop-domain` header) is not covered by HMAC verification, allowing shop attribution spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop` (and `topic`/`webhook_id`) values used by the host application to identify which merchant/tenant a webhook belongs to are taken from unauthenticated HTTP headers that sit entirely outside the signed payload.

### Finding Description
`Utils::HmacValidator.validate` verifies that `HMAC(secret, verifiable_query.to_signable_string) == received_hmac` [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no cryptographic binding to that signature [3](#0-2) .

`Registry.process` validates the HMAC and, if it passes, dispatches the handler using `request.topic` and passes `request.shop` straight into `WebhookMetadata` for the application to consume as the tenant identifier: [4](#0-3) 

The identity binding the code implicitly claims to hold is:
`verified_bytes(raw_body) == authenticated_tenant(shop_header)`

But the equality that actually holds is only:
`verified_bytes(raw_body) == raw_body`

`shop_header` (and `topic`/`webhook_id`) are parsed and trusted independently of what was cryptographically verified. Anyone who can reach the app's public webhook endpoint and possesses one valid `(raw_body, hmac)` pair — e.g., captured from a legitimate webhook delivery to their own shop, or from a Shopify "send test notification" for a topic they control as an app-installing merchant — can resend that exact body/hmac pair while substituting an arbitrary `X-Shopify-Shop-Domain` header value. `Utils::HmacValidator.validate` will still return `true` because it only re-hashes `@raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged `shop`, with the original (validly-signed) body content.

### Impact Explanation
This breaks the tenant-isolation boundary the gem is trusted to enforce for webhook processing: a value that host applications treat as an authenticated cross-tenant identifier (`shop`) can be forged independently of the signature that supposedly authenticates the whole request. Any app that uses `WebhookMetadata#shop` to decide which merchant's records to create, update, or delete (a documented, expected usage pattern shown in the gem's own webhook handler examples) can be made to apply another shop's/attacker-controlled webhook body under a victim shop's identity, causing cross-tenant data corruption or unauthorized mutation. This matches the High severity bar for "scope or expiry check bypass" / identity-binding bypass in a credential/tenant boundary.

### Likelihood Explanation
The webhook receiving endpoint is by design public (Shopify posts to it over the internet), and the header-vs-signed-body binding gap is a durable structural property of `Request#to_signable_string`/`Request#shop`, not an edge case. The only prerequisite is possession of one valid `(raw_body, hmac)` pair for any topic on the app — obtainable by any merchant who has installed the app, or by intercepting a delivery — after which the shop header can be freely substituted on repeated requests to the same public endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable representation used for webhook verification (as Shopify's own signature only covers the body, the gem should additionally treat these header-derived identifiers as sensitive and either (a) look up the expected shop/topic out-of-band via an authenticated session/store rather than trusting the header verbatim, or (b) explicitly document to consumers that `WebhookMetadata#shop` is unauthenticated header data and must not be used for tenant-scoping decisions without additional verification).

### Proof of Concept
```ruby
require "shopify_api"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":1,"note":"legit order for shop-a"}'
hmac = Base64.strict_encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
)

# Attacker captured (raw_body, hmac) from a real delivery to shop-a.myshopify.com,
# then replays it claiming it is for shop-b.myshopify.com:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,          # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "shop-b.myshopify.com", # forged tenant
  "x-shopify-webhook-id" => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because it only hashes raw_body.
# The handler receives WebhookMetadata(shop: "shop-b.myshopify.com", body: parsed legit body),
# even though "shop-b" never sent or was ever associated with this webhook.
```

### Citations

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
