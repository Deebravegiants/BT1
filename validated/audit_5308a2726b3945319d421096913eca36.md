Confirmed: `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) . `HmacValidator.validate` only checks the HMAC against `to_signable_string` (the body), never against the shop header [3](#0-2) , and `Registry.process` forwards the header-derived, unauthenticated `request.shop` straight into the handler payload after only checking the body HMAC [4](#0-3) .

### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, using a single per-app secret (`Context.api_secret_key`) shared across every shop that installs the app. The `shop` value that is handed to the app's webhook handler is read straight from the `x-shopify-shop-domain` header, which is not covered by the HMAC at all. This breaks the intended binding `HMAC-verified-shop == handler-attributed-shop`.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it, via `OpenSSL.secure_compare`, to the HMAC supplied in the `x-shopify-hmac-sha256` header [3](#0-2) . For webhook requests, `to_signable_string` is defined as just the raw body [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors are all read verbatim from HTTP headers that are never mixed into the signed string [5](#0-4) .

`Registry.process` performs exactly one check — `Utils::HmacValidator.validate(request)` — and then immediately builds `WebhookMetadata` using `request.shop` (the unauthenticated header value) as the tenant identifier passed to the app's business logic [4](#0-3) .

Because `Context.api_secret_key` is one static secret for the whole app (not per-shop), the HMAC over a given body is identical no matter which of the app's installed shops originally produced it. Any user who has installed the app on their own store (an "unprivileged internet user" from the perspective of any other merchant) can:
1. Receive one legitimate webhook delivery to their own shop and capture its raw body + `x-shopify-hmac-sha256` value.
2. Replay that exact body/HMAC pair to the app's public webhook endpoint, but substitute the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks the (unmodified) body against the (unmodified) HMAC — it never validates the shop header — so `Registry.process` invokes the app's handler with `shop: <victim-shop>`.

This lets an attacker forge webhook events that the host application will attribute to any other tenant of the same app, even though the event body/content did not originate from that tenant. This is the "shop authenticated versus shop stored/used as tenant key" identity-binding break: the equality that should hold is `verified_signer_shop == metadata.shop`, but the gem instead enforces only `HMAC(body) == signature`, with `metadata.shop` taken from unauthenticated input.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an attacker with no privileges beyond installing the app on their own store can cause the host application to process attacker-supplied webhook content under a victim merchant's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up and act using that shop's stored access token, update per-shop settings, or trigger shop-scoped side effects), this can lead to cross-tenant data corruption or actions being performed against a shop the attacker does not control.

### Likelihood Explanation
Likelihood is high for any app that exposes a public webhook endpoint (the standard integration pattern documented for this gem): any developer/merchant account can install the app to receive at least one legitimate webhook, and replaying a captured HTTP POST with one modified header is trivial. No secret, access token, or privileged access is required beyond normal app installation.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signed material verified against the HMAC, or otherwise cryptographically bind the header-derived `shop` value to the payload before trusting it — for example, by deriving/validating shop identity from a signed claim rather than the raw `x-shopify-shop-domain` header, or by requiring callers to additionally reconcile the header shop with a shop already known to be associated with that webhook subscription/session before invoking handlers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook with a generic/empty body, e.g. `orders/create` with body `{}` (as used in `test_process_with_new_format_headers`) [6](#0-5) .
2. Attacker captures the raw body (`{}`) and the `x-shopify-hmac-sha256` value Shopify computed with the app's shared `api_secret_key`.
3. Attacker POSTs to the app's webhook endpoint with the same body and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully since all required headers are present [7](#0-6) .
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because the body/HMAC pair is untouched [8](#0-7) .
6. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: {}, ...)` [9](#0-8) , causing the host app to treat the event as originating from the victim shop.

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
