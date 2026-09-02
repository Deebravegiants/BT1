### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). The shop header is therefore an unauthenticated field that is nonetheless trusted and forwarded to the host application's webhook handler as the tenant context.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it against the `hmac` value the caller supplies [1](#0-0) . For webhooks, `Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` / `Request#shop` are both simply read off the incoming HTTP headers (`x-shopify-hmac-sha256` / `shopify-hmac-sha256` and `x-shopify-shop-domain` / `shopify-shop-domain`) with no cryptographic relationship between the two [2](#0-1) .

`Registry.process` validates the HMAC and, once it passes, immediately trusts `request.shop` as the tenant identity and hands it to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop bound by HMAC == shop acted upon`. In this gem, the equality actually enforced is only `hmac(raw_body) == received_hmac`; the `shop` field used to build `WebhookMetadata` (and passed on to `WebhookHandler#handle`) [4](#0-3)  is never included in the signed material. Any entity that possesses one valid `(raw_body, hmac)` pair for a webhook delivered to their own shop can re-present that exact pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value. `HmacValidator.validate` will still return `true`, because it only checks `raw_body` against the secret, and `Registry.process` will dispatch the handler with the attacker-chosen `shop` value in `WebhookMetadata#shop`.

This is confirmed by the header-normalization logic, which shows `shop` is read purely from headers with no cross-check against the HMAC-signed payload [5](#0-4) , and by the test suite, which only exercises the header/body relationship in isolation without asserting any binding between `shop-domain` and the HMAC [6](#0-5) .

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing. Any host application that trusts `WebhookMetadata#shop` to select which merchant's data/session to operate on (a common and documented pattern, since this is exactly the field the library exposes for that purpose) can be tricked into writing or reading data under the wrong shop by an attacker who owns any single shop that has legitimate webhooks configured for the same app. This is a cross-tenant data-integrity/confidentiality issue at the webhook-processing layer, since the gem itself performs no verification that the claimed `shop` was the actual recipient/originator of the HMAC-signed payload.

### Likelihood Explanation
Exploitation only requires an attacker to install the app on their own (attacker-controlled) shop — a normal, unprivileged action — receive a genuine webhook (with a valid HMAC computed by Shopify using the app's secret, which the attacker never needs to know), and replay it to the app's public webhook endpoint with a modified `shop-domain` header. No access to `api_secret_key`, access tokens, or any other credential is required, only control of the webhook endpoint's public HTTP interface, making this a realistic, gem-level flaw rather than a host-app misuse issue.

### Recommendation
- Include the shop domain (and ideally other identifying headers such as `webhook-id`/`api-version`) in the HMAC-signed material, or otherwise cryptographically bind the claimed shop to the verified payload, before exposing it via `Request#shop`/`WebhookMetadata#shop`.
- At minimum, document prominently that `shop` is unauthenticated and require host apps to cross-check it against a known/registered shop list before trusting it for any tenant-scoped operation — but the safer fix is to make `HmacValidator` bind the header value that callers key their tenant logic on.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify send a genuine webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (a valid HMAC of `B` using the app's real secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures `(B, H)` and resends a request to the app's webhook endpoint with the same body `B` and hmac header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process(request)` calls `HmacValidator.validate(request)`, which only checks `hmac(B) == H` — this passes [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the host app to process attacker-controlled webhook content under the victim shop's tenant context.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** test/webhooks/request_test.rb (L59-76)
```ruby
      def test_accessor_values_with_new_format_headers
        hmac_value = Base64.encode64("test_hmac_bytes")
        headers = {
          "shopify-topic" => "orders/create",
          "shopify-hmac-sha256" => hmac_value,
          "shopify-shop-domain" => "test-shop.myshopify.com",
          "shopify-api-version" => "2024-01",
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
        }

        request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers)

        assert_equal("orders/create", request.topic)
        assert_equal("test-shop.myshopify.com", request.shop)
        assert_equal("2024-01", request.api_version)
        assert_equal("b1234-eefd-4c9e-9520-049845a02082", request.webhook_id)
        assert_equal(Digest.hexencode(Base64.decode64(hmac_value)), request.hmac)
      end
```
