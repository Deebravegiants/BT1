Confirmed: `WebhookHandler` and `WebhookMetadata` in `lib/shopify_api/webhooks/webhook_handler.rb` take `shop` from `WebhookMetadata.new(shop: request.shop, ...)` with no re-validation against the HMAC-signed content, and `ShopValidator` is never invoked in the webhook processing path. This confirms the gap.

### Title
Webhook Shop-Domain Header Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's webhook handler from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Registry.process` validates only covers the raw request body. This breaks the identity binding `bytes verified == bytes acted on`: the signature proves the body came from Shopify (for *some* shop), but the `shop` value the handler trusts to attribute that body to a tenant is never part of the signed material and can be swapped by anyone who can reach the webhook endpoint.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over that signable string and compares it to the `hmac-sha256` header [2](#0-1) . The `shop` accessor, however, is read straight from the `shop-domain` header with no cryptographic binding to the body or the HMAC [3](#0-2) .

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app-defined handler: `raise ... unless Utils::HmacValidator.validate(request)` followed by `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [4](#0-3) . No component in this path (not `Registry`, not `WebhookHandler`, not `ShopValidator`) cross-checks that the `shop-domain` header is consistent with anything the HMAC actually covers [5](#0-4) . `ShopValidator`, which does exist in the gem for sanitizing shop domains elsewhere, is never invoked in this webhook flow [6](#0-5) .

**Binding broken:** `shop domain trusted by handler == shop domain covered by HMAC` does not hold; in reality `shop domain trusted by handler == arbitrary attacker-supplied header`, while `shop domain covered by HMAC == "" (not covered at all)`.

**Attack sequence:**
1. Attacker installs the target app on their own store (`attacker.myshopify.com`), a shop they legitimately control, and triggers any registered webhook topic (e.g. `orders/create`). Shopify delivers a POST to the app's webhook endpoint with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's `client_secret`.
2. Attacker captures this raw request: body + valid HMAC header.
3. Attacker (or any unprivileged internet user who can reach the public webhook endpoint) replays the exact same body and HMAC header, but substitutes `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC — the shop header is never part of that computation.
5. `Registry.process` calls the app's handler with `WebhookMetadata` claiming `shop: "victim.myshopify.com"`, even though the body content was generated for the attacker's own shop.

### Impact Explanation
This is a cross-tenant identity confusion in the gem's own webhook-processing primitive: an entity that only controls its own (attacker) shop can cause the app's business logic to process attacker-supplied data under a victim shop's identity. Depending on how the host application keys storage/side-effects off `WebhookMetadata#shop` (order records, inventory updates, subscription state, etc.), this can corrupt or overwrite another merchant's data — a cross-tenant access impact, which is in the Critical impact category defined for this engagement.

### Likelihood Explanation
High. The gem provides no documentation or code that instructs developers to independently verify `data.shop` against a known/trusted set of shops before acting on webhook data; `docs/usage/webhooks.md` presents `Registry.process` as sufficient verification ("This will verify the request did indeed come from Shopify...") [7](#0-6) . Any app following the documented pattern inherits this gap. The only prerequisite is the ability to install the app on any shop (self-service in the Shopify ecosystem) and to send an HTTP request to the app's public webhook route — no privileged credential, secret, or victim interaction is required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable material, or, at minimum, have `Registry.process`/`WebhookMetadata` treat `shop` as untrusted and require host applications to validate it via `ShopValidator.sanitize!` against known installed shops before dispatching to the handler. Document explicitly that `request.shop` is not covered by the HMAC signature.

### Proof of Concept
Using the gem's own test fixtures as a basis [8](#0-7) :
```ruby
body = "{\"id\":1}"
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

# Step 1: attacker captures a genuine webhook for their own shop
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker.myshopify.com",
}

# Step 2: attacker replays it, only changing the shop-domain header
spoofed_headers = headers.merge("x-shopify-shop-domain" => "victim.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: spoofed_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (HMAC only covers `body`)
# => handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", ...))
```
The handler receives attacker-controlled data attributed to `victim.myshopify.com`, despite the attacker never having access to the victim shop or its credentials.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-24)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```

**File:** lib/shopify_api/utils/shop_validator.rb (L20-64)
```ruby
      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
