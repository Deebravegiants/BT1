### Title
Webhook shop-domain/topic spoofing due to HMAC covering only the raw body, not headers - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the **raw request body**. The `shop` (tenant identity) and `topic` values that are dispatched to the app's handler come from HTTP headers that are **not part of the signed payload**. Any party who can obtain one legitimately-signed `(body, hmac)` pair for the app (e.g., by owning a store that has the app installed and capturing a webhook Shopify sends them) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` (and/or `topic`) header, and the request will still pass HMAC validation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers and are never included in the signable string: [2](#0-1) 

`Registry.process` validates only this body-only HMAC, then immediately trusts `request.topic` and `request.shop` to route/dispatch the event: [3](#0-2) 

This is exactly the "field acted on but not covered by the HMAC" binding break: the equality the code implicitly assumes is
`shop_in_HMAC_signed_bytes == shop_used_for_tenant_dispatch`,
but in reality the HMAC only signs `raw_body`, while `shop` (the tenant key) and `topic` come from unauthenticated headers. The documented processing flow explicitly claims the call "will verify the request did indeed come from Shopify" and then dispatch by shop/topic, reinforcing that host apps are expected to trust the gem's validation of both fields: [4](#0-3) 

The test suite even demonstrates that HMAC validation happens over the raw JSON body independent of headers, and shows the shop/topic values are read from separate header fields that could be forged: [5](#0-4) 

### Impact Explanation
An attacker who operates their own shop (an unprivileged multi-tenant participant of the same app) receives real, validly-signed webhooks from Shopify for their own store. Because the signature covers only the body, the attacker can replay a captured `(raw_body, hmac)` pair to the app's public webhook endpoint while setting the `shop-domain` header to a victim shop's domain (and/or changing `topic`). `Registry.process` will accept it as authentic and hand the handler a `WebhookMetadata` claiming to be from the victim shop with attacker-controlled `body`/`topic`. Depending on how the host app scopes data updates by `data.shop`, this enables cross-tenant data corruption/injection — e.g., writing attacker-controlled order/product/customer data into the victim shop's tenant records, or triggering shop-scoped side effects (billing, app-uninstalled handling, etc.) against a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that has more than one installing shop (the norm for public/multi-tenant Shopify apps): any store owner who installs the app can trivially capture legitimate webhook deliveries sent to their own endpoint (they control DNS/hosting for their callback URL, or can simply log the raw request) and replay them with a modified `shop-domain` header, since no part of the gem's validation binds `shop` to the HMAC.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the bytes that are HMAC-verified, or otherwise cryptographically bind them to the body (e.g., validate that the `shop` header matches a shop for which this specific webhook subscription was registered before dispatching), rather than trusting header values that sit outside the HMAC-protected payload.

### Proof of Concept
1. App shop A installs the app; Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>` and some `raw_body`.
2. Attacker (owner of shop A) captures this exact `raw_body` and `x-shopify-hmac-sha256` value.
3. Attacker sends a new HTTP request to the same webhook endpoint with the identical `raw_body`/`hmac` but `x-shopify-shop-domain: shop-victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers as-is: [6](#0-5) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — it succeeds because the body wasn't modified: [7](#0-6) 
6. The handler receives `WebhookMetadata` with `shop: "shop-victim.myshopify.com"`, and the host app processes/records attacker-controlled data as belonging to `shop-victim`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** test/webhooks/registry_test.rb (L266-302)
```ruby
      def test_process_with_new_format_headers
        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal("b1234-eefd-4c9e-9520-049845a02082", data.webhook_id)
            assert_equal("2024-01", data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)

        assert(handler_called)
      end
```
