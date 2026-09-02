This confirms the vulnerable flow: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are all pulled from unauthenticated HTTP headers via `shopify_header` [2](#0-1) . `HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC [3](#0-2) , so it never covers the `shop` header. `Registry.process` accepts the request once HMAC validates and forwards `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identity [4](#0-3) [5](#0-4) . The test fixture confirms the HMAC is computed only over the body (`"{}"`) while `shop-domain` is a separate, independent header value [6](#0-5) .

This exactly matches the requested bug class: "a field acted on but not covered by the HMAC." The `shop` value is acted upon (used as the tenant identity passed to the app's webhook handler) but is not part of the HMAC-covered signable string, breaking the intended binding `shop_verified == shop_used_by_handler`.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field entirely from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature verified by `Utils::HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). Any request bearing a body + HMAC pair that was legitimately produced by Shopify for *one* shop can be replayed with an attacker-controlled `shop-domain` header, and it will still pass HMAC validation, causing the app's webhook handler to process the payload under a different, spoofed shop identity.

### Finding Description
`Registry.process` is the sole gate for webhook authenticity: `raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` [4](#0-3) . `HmacValidator.validate_signature` recomputes the signature strictly from `verifiable_query.to_signable_string` [7](#0-6) , and `Request#to_signable_string` is simply `@raw_body` [1](#0-0) .

Meanwhile, `Request#shop`, `#topic`, and `#webhook_id` are read straight out of attacker-controllable headers with no cryptographic binding to the HMAC-verified body: `T.cast(shopify_header("shop-domain"), String)` [8](#0-7) . Once `process` confirms the body's HMAC is valid, it unconditionally trusts these header-derived fields and constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` for the app's handler [9](#0-8) , which apps use as the authoritative tenant identifier to look up/mutate that shop's records (this is the gem's documented usage pattern) [10](#0-9) .

The identity binding that should hold is: `shop_that_signed_the_hmac == shop_the_handler_believes_it_is_processing_for`. Because `shop` is outside the signable string, this equality is not enforced — the HMAC only proves "Shopify sent this body," not "Shopify sent this body for shop X."

### Impact Explanation
An attacker who controls (or has installed the app on) shop A can capture a legitimate webhook body + valid HMAC that Shopify sent for shop A, then resend that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with shop B's domain. `HmacValidator.validate` still returns `true` because the body is untouched, so `Registry.process` invokes the handler with `shop: "shop-B.myshopify.com"` even though the payload actually originated from/for shop A. If the app's handler uses this `shop` value to load shop B's session/access token and act on shop B's store (e.g., writing shop-A-controlled order/product data into shop B's records, or triggering shop-B-scoped side effects using shop-A data), this is a cross-tenant data-integrity break driven entirely by an unauthenticated header value passing as a trusted identity.

### Likelihood Explanation
Any actor able to install the target app on a shop they control (a normal, unprivileged step for any Shopify merchant/developer) can generate authentic webhook bodies/HMACs for that shop at will (e.g., by trivial actions like updating an order), then replay them against the app's public webhook endpoint with a forged `shop-domain` header — no access token, `client_secret`, or privileged access is required. This is purely a gap in what the HMAC is defined to cover in `Webhooks::Request`.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-covered signable string, or otherwise cryptographically tie the header-derived shop to the signed payload, e.g., include the relevant headers in `to_signable_string`, or require the handler to validate `request.shop` against an out-of-band store lookup keyed by a value that is itself covered by the signature. At minimum, document and enforce that consumers must independently confirm `request.shop` corresponds to a shop for which they already have an active session/installation before trusting the payload for that tenant.

### Proof of Concept
```ruby
# Attacker owns/installs app on "attacker-shop.myshopify.com" and receives
# a legitimate webhook with body B and its real HMAC-SHA256, e.g. as in
# test/webhooks/registry_test.rb setup:
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, "{}")

# Attacker now POSTs the SAME body + HMAC to the app's webhook endpoint,
# but swaps the shop-domain header to the victim shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac), # still valid, body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by hmac
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body "{}" hmac matches),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
#    is invoked, i.e., the app processes attacker-supplied data under the victim's identity.
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

**File:** test/webhooks/registry_test.rb (L14-30)
```ruby
        @shop = "shop.myshopify.com"

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
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
