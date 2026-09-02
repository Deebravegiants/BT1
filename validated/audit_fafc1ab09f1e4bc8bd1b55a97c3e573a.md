Confirming the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers via `shopify_header` [2](#0-1) . `Registry.process` validates only the HMAC over that body via `Utils::HmacValidator.validate(request)` and then dispatches using `request.topic`/`request.shop` taken straight from headers [3](#0-2) .

### Title
Webhook shop/topic identity not covered by HMAC signature enables cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw JSON body for HMAC verification, while the `shop-domain`, `topic`, `api_version`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to route and label the event are taken from unauthenticated headers.

### Finding Description
The identity binding that should hold is: `hmac_signed_content == content_used_to_attribute_the_webhook_to_a_tenant_and_topic`. In this gem that equality is broken. `Utils::HmacValidator.validate` recomputes the signature purely from `verifiable_query.to_signable_string`, and for webhooks that method returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read straight from the `shopify-*`/`x-shopify-*` headers with no cryptographic tie to the signed body [2](#0-1) . `Registry.process` validates the HMAC, then immediately trusts `request.topic` and `request.shop` (both header-derived) to look up the handler and build `WebhookMetadata` passed to the app's handler [3](#0-2) .

Because many legitimate webhook bodies are small/generic (e.g. the mandatory `shop/redact`, `customers/redact`, `customers/data_request` payloads, or webhooks with an empty `{}` body as shown in the test fixtures) [4](#0-3) , a merchant who has legitimately installed the app on their own store receives a validly-signed webhook (correct HMAC over that body, computed by Shopify with the app's real `client_secret`). That same body+HMAC pair remains valid no matter which `shop-domain`/`topic`/`webhook_id` headers accompany it, because those fields are not part of the signed content. Replaying that captured body+HMAC to the app's webhook endpoint with a different `shop-domain` header value causes `Registry.process` to accept it as an authentic webhook for a different shop or topic.

### Impact Explanation
This crosses a tenant boundary: the app's webhook handler acts on `WebhookMetadata#shop`/`topic` believing them to be authenticated, when in this gem they are not bound to the HMAC. A host app handler that keys any per-shop state (uninstall/redact processing, data deletion, entitlement changes) off `request.shop`/`request.topic` can be tricked into performing that action against a shop the attacker doesn't own, or invoking a different topic's handler with a replayed generic body — a cross-tenant impact.

### Likelihood Explanation
Requires only an unprivileged attacker who has installed the app on any shop they control (a normal, unprivileged merchant onboarding) and the ability to replay/craft an HTTP POST to the app's public webhook endpoint with modified headers — no access to the app's `api_secret_key` or any other shop's credentials is needed, since the header values were never protected by the signature in the first place.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content (or otherwise cryptographically bind them, e.g., by having `to_signable_string` incorporate the headers alongside the raw body) so `Utils::HmacValidator.validate` fails whenever those identity fields are altered, matching the same principle Shopify already applies to the OAuth `AuthQuery#to_signable_string`, which explicitly signs `shop` together with the rest of the query [5](#0-4) .

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a `customers/redact` webhook, capturing the raw body (commonly `"{}"`) and the `x-shopify-hmac-sha256` header Shopify computed for it.
2. Attacker (or a malicious intermediary controlling the delivery) POSTs to the app's webhook endpoint reusing that exact raw body and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: shop/redact`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers (only checks presence, not binding) [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body against the HMAC [7](#0-6) , then dispatches the handler registered for `victim-shop`'s topic with `shop: "victim-shop.myshopify.com"` in the `WebhookMetadata` passed to the app's handler [8](#0-7) .

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

**File:** test/webhooks/registry_test.rb (L284-298)
```ruby
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
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
