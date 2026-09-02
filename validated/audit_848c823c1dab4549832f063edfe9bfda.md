### Title
Webhook shop identity (and topic/api_version/webhook_id) not covered by HMAC signature enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` fields used to route and process the webhook are read from unauthenticated HTTP headers. This breaks the binding "shop authenticated == shop acted upon," letting an attacker who can obtain one validly-HMAC-signed webhook payload for their own store replay it with a forged `shopify-shop-domain` header to make the receiving app attribute the webhook's data to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then dispatches the handler using the unauthenticated `request.shop` (and `request.topic`, etc.) as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` signs/verifies exactly `verifiable_query.to_signable_string`, which for webhooks is just the body bytes — the shop domain is never part of what's authenticated: [4](#0-3) 

The equality this breaks: `shop authenticated by HMAC` should equal `shop the handler processes data for`. Here, only `raw_body` is authenticated; `shop` is parsed independently of the signature, so `shop_in_signed_bytes != shop_used_for_dispatch` is possible whenever an attacker controls the HTTP request headers reaching the app's webhook endpoint but reuses a body+HMAC pair that was legitimately generated (e.g., for their own store, which any unprivileged user can install the app on and trigger).

The test suite itself demonstrates that the HMAC is computed over the body independent of shop, topic, or webhook id headers: [5](#0-4) 

### Impact Explanation
This is a cross-tenant confusion vector: an unprivileged attacker who installs the target app on their own (attacker-controlled) shop can legitimately receive a validly-signed webhook (body + HMAC) from Shopify. If the attacker can influence or replay the HTTP request delivered to the app's webhook endpoint (e.g., via any proxy, replay, or header-manipulation opportunity in the delivery path) while keeping the same body/HMAC, the app-side `Registry.process` will accept the HMAC as valid and treat the payload as belonging to whatever `shop` domain the header claims — a shop the attacker does not control. Handlers that use `data.shop` to select tenant DB rows, trigger side effects, or make decisions "per shop" (e.g., `shop/redact`, `customers/data_request`, order/customer webhooks) can then mutate or expose another merchant's data under attacker-supplied content, i.e., cross-tenant access/writes.

### Likelihood Explanation
Exploitation requires the attacker to control (or be able to tamper with) the headers of an otherwise validly-signed webhook delivery. This gem's `Request` class trusts caller-supplied headers on its own without any independent verification, so any host application that forwards attacker-influenced headers (proxies, gateways, load balancers not stripping/re-setting these headers, or apps that expose raw request parsing) into `Webhooks::Request.new` inherits this gap. Likelihood is moderate — it depends on the app's request-handling that surrounds this gem, but the gem's own signable-string design is the root cause and provides no defense-in-depth against header spoofing of `shop`/`topic`/`webhook_id`.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` header values in the HMAC-signable string (or otherwise cryptographically bind them to the signed body), matching the pattern already used for OAuth's `AuthQuery#to_signable_string`, which signs `code`, `host`, `shop`, `state`, and `timestamp` together: [6](#0-5) 

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) with body `B`. Shopify computes `HMAC(secret, B)` and delivers headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: H`.
2. Attacker (or a component in the delivery path they control) intercepts/replays the request to the app's webhook endpoint but rewrites the header to `shopify-shop-domain: victim-shop.myshopify.com`, keeping body `B` and hmac `H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — matching `H`, since the header change is irrelevant to `to_signable_string`. [3](#0-2) 
4. The webhook handler executes with `data.shop == "victim-shop.myshopify.com"` even though the payload originated from the attacker's shop, causing the app to process attacker-controlled content under the victim's tenant identity.

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

**File:** test/webhooks/registry_test.rb (L280-300)
```ruby
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
