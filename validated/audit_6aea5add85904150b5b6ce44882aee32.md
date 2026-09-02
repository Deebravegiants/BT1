### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing shop/topic identity spoofing on an otherwise-authentic payload - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs/validates only the raw request body via HMAC, while `shop`, `topic`, `webhook_id`, and `api_version` are read from separate, unauthenticated HTTP headers and handed to the webhook handler as trusted tenant/routing identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) . `Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it to the `hmac` value extracted from the `hmac-sha256` header [2](#0-1) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with `request.shop`, `request.topic`, and `request.webhook_id` taken straight from headers [3](#0-2) , and those accessors read directly from `@headers` with no cross-check against the signed bytes [4](#0-3) .

This is the ERC20-style inconsistency pattern from the report: the interface (`VerifiableQuery`) implies "hmac verifies this request," but only a subset of the identity-bearing fields (the body) is actually bound to the signature — the `shop-domain` header, the field the handler uses as the tenant key, is not. Concretely: **binding claimed = (`hmac` verifies `shop`, `topic`, `body`)**, but **binding actual = (`hmac` verifies only `body`)**. Any request whose body bytes match a previously-observed, validly-signed payload (e.g., a benign/empty-body webhook topic, or any topic where the body content is attacker-guessable/constant, such as `app/uninstalled` pings with predictable minimal JSON, or any webhook the attacker's own test/dev shop legitimately receives) can have its `shop-domain` and `topic` headers replaced arbitrarily while the HMAC check still passes, because those headers are never part of `to_signable_string`.

### Impact Explanation
This lets an attacker who can obtain one validly-signed webhook body from Shopify (e.g., by installing the app on their own shop and capturing/replaying a real inbound webhook they legitimately receive) submit it to the app's public webhook endpoint claiming an arbitrary `shop-domain`/`topic`. Because `Registry.process` passes `request.shop` and `request.topic` unchecked into `WebhookMetadata` for the host application's handler [5](#0-4) , this can trigger cross-tenant processing: the handler will act as if shop B (a different merchant) sent the event, when in fact the cryptographically-authenticated content only proves the attacker's own shop A produced that body. Depending on how the host app uses `data.shop`/`data.topic` (e.g., to look up records, trigger side effects, or infer install/uninstall state for another tenant), this crosses the tenant boundary — matching the "Critical: cross-tenant access" impact category.

### Likelihood Explanation
Exploitability is constrained: the attacker needs a body+HMAC pair that is actually valid for the secret, which in practice means owning/controlling a shop that installs the app and receiving at least one webhook from Shopify. Many webhook topics have shop-specific or randomized body content, limiting where identical bodies are reusable across "topic"/"shop" claims, but topics with minimal/predictable bodies (e.g., some `app/uninstalled`, `shop/redact`, or bulk-operation completion pings with fixed JSON structure) make this practical. This is a design gap in the gem's `VerifiableQuery` contract for webhooks rather than a purely theoretical issue, since the library explicitly authenticates the object and callers reasonably assume all `Request` accessors are trustworthy once `HmacValidator.validate` passes.

### Recommendation
Bind the tenant/routing identity fields into the signable string (or otherwise cryptographically bind them), e.g., include `shop-domain` and `topic` in `to_signable_string`, or require callers to separately verify `request.shop` against a known/registered list of installed shop domains before trusting it — and document this requirement prominently if the header cannot be included in the signature for compatibility with Shopify's server-side signing (Shopify signs body-only by design). At minimum, `Registry.process` should not implicitly treat `request.shop` as authenticated; the gem should expose a clear signal (or perform a check) that `shop` is unauthenticated header data.

### Proof of Concept
1. Attacker installs the app on a shop they control (`attacker.myshopify.com`) and captures a legitimately Shopify-signed webhook delivery for a topic with fixed/minimal body content, e.g. body `"{}"` with header `shopify-hmac-sha256: <valid-hmac-for-"{}">` and `shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body and HMAC header to the app's public webhook endpoint but sets `shopify-shop-domain: victim.myshopify.com` and/or a different `shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body without error [6](#0-5) ; `Utils::HmacValidator.validate(request)` succeeds because it only checks the body bytes against the secret [7](#0-6) .
4. `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"` despite the payload never having been signed for that shop, as shown by the test harness constructing/validating webhook requests purely from `raw_body` + headers with no shop binding check [8](#0-7) .

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
