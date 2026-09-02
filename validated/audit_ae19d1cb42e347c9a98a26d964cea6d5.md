Confirmed: `Registry.process` at [1](#0-0)  validates only the HMAC over `to_signable_string` (the raw body) and then dispatches to the handler using `request.shop` and `request.topic`, both of which are read straight from HTTP headers that are **not part of the signed payload**.

### Title
Webhook `shop` (and `topic`) identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body via `to_signable_string`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers and never enter the HMAC computation. `Registry.process` trusts these header-derived values to route the payload and to identify the originating shop, breaking the equality that should hold between "the shop cryptographically bound to this authenticated payload" and "the shop passed to the app's webhook handler."

### Finding Description
`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns `@raw_body` only: [2](#0-1)  and [3](#0-2) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors simply read HTTP headers with no cryptographic tie to the body: [4](#0-3) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body integrity) before handing `request.shop` and `request.topic` straight to the app's handler: [5](#0-4) .

Because `shop-domain` is outside the signed bytes, the equality that the design implicitly assumes — `hmac_valid(body) == shop_header_is_authentic_for(body)` — does not hold. An attacker who is a legitimate (unprivileged) merchant of the app receives genuinely-signed webhooks for their own shop A (valid `hmac-sha256` computed with the app's real `api_secret_key` over their own event body). They can replay that exact `raw_body` + `hmac-sha256` value to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop B. Since the HMAC only certifies the body bytes, `HmacValidator.validate` still returns `true`, and `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "shopB.myshopify.com", ...)` even though the actual signed content belongs to shop A.

### Impact Explanation
This is a cross-tenant identity-binding break: the app's webhook handler will process/store data under a shop identity that was never authenticated for that data. Depending on how the host app's handler uses `data.shop` (e.g., looking up per-shop settings, crediting orders, updating per-tenant records), this can lead to cross-tenant data corruption or disclosure — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint plus possession of one legitimately-signed webhook body (trivially obtainable by installing the app on one's own shop and capturing any webhook delivery, or via `test/webhooks/registry_test.rb` style payloads, e.g. `raw_body: "{}"`, which is trivially reusable — note the fixed `"{}"` body used across topics in [6](#0-5) ). No secret key, access token, or privileged account is required.

### Recommendation
Include `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) in the signable content that `HmacValidator` verifies, or otherwise cryptographically bind the header values to the payload before `Registry.process` trusts them for routing/identification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, capturing `raw_body` and the genuine `x-shopify-hmac-sha256` header.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` from the spoofed header: [7](#0-6) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (genuine) signature: [8](#0-7) .
5. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)`, processing attacker-controlled event data under the victim shop's identity: [9](#0-8) .

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** test/webhooks/registry_test.rb (L16-33)
```ruby
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
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```
