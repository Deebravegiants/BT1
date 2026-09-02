### Title
Webhook shop/topic identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw body only, while the shop domain, topic and webhook id used by `ShopifyAPI::Webhooks::Registry.process` to route and label the event to the host application are taken from unauthenticated HTTP headers that are never included in the signed bytes. The gem's own documentation still states that `Registry.process` "will verify the request did indeed come from Shopify," creating a mismatch between what is cryptographically proven (body integrity/origin) and what is exposed to the app as trusted per-tenant identity (`shop`).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it against the `hmac` header: [2](#0-1) 

`Request#shop`, `#topic`, and `#webhook_id` are parsed straight from HTTP headers with no cryptographic binding to the body or the HMAC: [3](#0-2) 

`Registry.process` validates only the HMAC, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The library's own docs describe `Registry.process` as verifying "the request did indeed come from Shopify," and document `data.shop` as "The shop domain of the webhook" — i.e., a trusted, authenticated identity field for the app to key tenant data on: [5](#0-4) 

The identity binding broken is: **shop-domain header authenticated by the gem's `Registry.process` contract ("did indeed come from Shopify") vs. shop-domain value that is actually covered by the HMAC (none — only the body is signed)**. Because `api_secret_key`/`client_secret` is shared across every shop that has installed the same app, any shop that has installed the app (an unprivileged merchant, requiring no special access) can receive a legitimate signed webhook for their own store, then replay that exact body + `x-shopify-hmac-sha256` header to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header for a victim shop. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` dispatches the handler with the attacker-chosen `shop` value trusted as authentic.

### Impact Explanation
If the host application relies on the gem's documented guarantee that a webhook processed via `Registry.process` legitimately originates from the named `shop`, cross-tenant data confusion is possible: an attacker-controlled webhook body can be attributed to any other shop that uses the same app, allowing writes/updates to be applied against a victim tenant's session/store data, or exfiltration of information intended to be scoped to that tenant. This matches the Critical "cross-tenant access" category, since the shop identity is the sole tenant boundary the gem exposes to callers.

### Likelihood Explanation
Any merchant who installs the app (a normal, unprivileged action available to any internet user for public apps, or a developer-store owner for private/custom apps) automatically receives correctly-HMAC'd webhooks from Shopify and can capture the body + valid HMAC header pair. Forging the `x-shopify-shop-domain` header on a replayed HTTP request requires no cryptographic material beyond what a legitimately installed merchant already possesses, and the HMAC check in this gem will still pass.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified against the HMAC, or independently verify that the `shop` header corresponds to a shop with an active, registered webhook subscription (matching `webhook_id`) before trusting it in `WebhookMetadata`. At minimum, document explicitly that `Registry.process` only authenticates the request body's origin and that `data.shop`/`data.topic`/`data.webhook_id` are NOT covered by the HMAC and must be independently validated by the host application against its own webhook registration records before being used as a tenant key.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on `victim-shop.myshopify.com`, both sharing the same `api_secret_key`.
2. Attacker triggers/receives a legitimate webhook for their own shop, capturing `raw_body` and the `x-shopify-hmac-sha256` header Shopify computed over that body.
3. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers normally [6](#0-5) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the signature only covers `raw_body` [7](#0-6) .
6. The handler is invoked with `WebhookMetadata` reporting `shop: "victim-shop.myshopify.com"`, which the host app treats as authenticated per the documented contract, resulting in cross-tenant processing.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
