### Title
Webhook `shop` (and other Shopify headers) are not covered by the HMAC signature, allowing cross-tenant attribution spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the webhook HMAC over the raw JSON body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` to attribute the payload to a specific merchant are taken from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/compares the HMAC exclusively over that string: [1](#0-0) [2](#0-1) 

But `shop` (and `topic`, `webhook_id`, `api_version`) are read straight from HTTP headers, independent of the signed bytes: [3](#0-2) [4](#0-3) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body integrity) before dispatching `request.shop` to the app's handler as the tenant identifier: [5](#0-4) 

The equality the gem is supposed to guarantee is:
`shop_bound_by_hmac == shop_used_for_tenant_attribution`

In reality the HMAC binds only the body bytes; it says nothing about the `shop-domain` header. So the equality actually enforced is `body_bytes_verified == body_bytes_parsed`, while `shop` is trusted without being part of that verified set — the same class of defect as the report's `fuses`/`expiry` parameters being applied to a name (`wrap`) without being bound by the verification that covers only the base-domain case. Here, the "shop" field acted upon by the handler is not bound by the same cryptographic check that covers the body.

This directly contradicts the gem's own documentation, which states that `Registry.process` "will verify the request did indeed come from Shopify" — implying the whole webhook, including its shop attribution — when in fact only the body content is verified: [6](#0-5) 

### Impact Explanation
An unprivileged internet user who controls network delivery between Shopify and the app's webhook endpoint for their own legitimately-installed shop (e.g., via a reverse proxy or middlebox they operate in front of their own webhook callback URL) receives a genuine, correctly-HMAC-signed webhook body from Shopify for their own shop. Because the `shop-domain` header is excluded from the signed content, they can rewrite that header to name a victim shop while keeping the original valid `hmac-sha256`/body pair intact, and forward it to the app's shared webhook endpoint. `Registry.process` will pass the HMAC check (body integrity holds) and dispatch `WebhookMetadata` with the victim's `shop` value to the app's handler, which stores/acts on the data believing it originated from the victim tenant. This is a cross-tenant data-integrity/attribution bypass in a High-Critical band depending on what the host handler does with `data.shop` (e.g., writing order/customer data under the wrong shop's session/store).

### Likelihood Explanation
Requires no possession of `api_secret_key`, access token, or any Shopify credential — only that the attacker be a legitimately-installed merchant/tenant of the target app who can manipulate traffic in front of their own webhook receiver endpoint (a capability entirely within an unprivileged user's control for a shared, publicly reachable webhook URL). No TLS interception of Shopify's traffic is needed since the attacker only needs to intercept/modify requests reaching *their own* app instance's public endpoint before they hit the gem's `Registry.process`.

### Recommendation
Bind the `shop` (and `topic`/`webhook_id`/`api_version`) header values into the HMAC-verified signable content, or otherwise cryptographically tie the header-derived tenant identity to the signed body (e.g., include a canonicalized header+body string in `to_signable_string`), so `Registry.process` cannot dispatch attacker-controlled tenant attribution alongside a validly-signed body.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and sits in front of their app's shared webhook endpoint (e.g. via a proxy they control before the request reaches the Rails/Sinatra app using this gem).
2. Shopify delivers a legitimate webhook: body `{"id":123,...}`, headers `x-shopify-hmac-sha256: <valid-for-body>`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker rewrites only the `x-shopify-shop-domain` header to `victim.myshopify.com`, leaving body and `hmac-sha256` untouched, and forwards the request to the app endpoint.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and `ShopifyAPI::Webhooks::Registry.process(request)` validate the HMAC successfully (`Utils::HmacValidator.validate`, which only checks the body) and call the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: {...}, ...)`, causing the app to process attacker-supplied data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
