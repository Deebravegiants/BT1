### Title
Cross-tenant webhook shop/topic spoofing — `Utils::HmacValidator` only signs the raw body, not the `shop`/`topic` headers used for tenant routing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity fields (`shop`, `topic`, `webhook_id`, `api_version`) directly from unauthenticated HTTP headers, while its HMAC-signable payload is only the raw request body. `Webhooks::Registry.process` trusts `request.shop`/`request.topic` after validating only that body-HMAC, so the binding `hmac-verified body == claimed shop/topic` never actually holds.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers that are never part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` runs this check and then unconditionally forwards the header-derived `shop`/`topic` to the handler: [4](#0-3) 

So the equality the library implicitly claims to guarantee is:
`hmac_valid(request) == true` implies `request.shop` is the shop that actually produced `request` (and by extension `request.topic`).

In reality the equality that holds is only:
`hmac_valid(request) == true` implies `raw_body` was signed by *some* holder of `api_secret_key` — with no constraint on which shop, topic, or webhook id is attached to that body.

Since `api_secret_key` is the app's single client secret shared across every installing shop (not a per-shop secret), any shop that installs the app — including one owned by the attacker — can generate a genuinely-signed webhook body/HMAC pair. The attacker can then submit that same `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` / `shopify-topic` headers to point at a victim shop; `HmacValidator.validate` still passes because it never looks at those headers.

### Impact Explanation
Any host application relying on this gem's `Webhooks::Registry.process` to determine *which shop* a webhook event belongs to (session/tenant lookup, triggering mandatory `shop/redact`, `customers/redact`, `customers/data_request`, or `app/uninstalled` side effects, etc.) can be made to process attacker-supplied data under a victim shop's identity. This is a cross-tenant access issue: the library's own validation step gives host apps false confidence that `request.shop`/`request.topic` are attacker-uncontrollable once the HMAC check passes.

### Likelihood Explanation
Exploitation only requires the attacker to be able to install the target app on a shop they control (a normal, unprivileged developer/merchant action) and to be able to reach the app's public webhook HTTP endpoint directly with modified headers — no access to `api_secret_key`, access tokens, or the victim's credentials is needed.

### Recommendation
Bind the tenant-identifying fields into the signed payload domain (e.g., include `shop`, `topic`, `webhook_id`, and `api_version` in `to_signable_string`, or otherwise cryptographically bind headers to the body) so that `HmacValidator.validate` actually authenticates the full claim `(shop, topic, body)` rather than the body alone.

### Proof of Concept
```ruby
require "shopify_api"

secret = ShopifyAPI::Context.api_secret_key
body = '{"id":1}'
hmac = Base64.encode64(OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, body))

# 1. Attacker's own shop legitimately triggers this (body, hmac) pair via a real webhook delivery.
# 2. Attacker replays the exact same body/hmac but swaps the shop-domain header:
forged_headers = {
  "shopify-topic" => "customers/redact",
  "shopify-hmac-sha256" => hmac,
  "shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, not covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Utils::HmacValidator.validate(request) # => true, despite shop being forged
ShopifyAPI::Webhooks::Registry.process(request) # handler receives shop: "victim-shop.myshopify.com"
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
