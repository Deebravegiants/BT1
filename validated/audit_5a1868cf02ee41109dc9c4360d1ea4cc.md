### Title
Webhook HMAC only signs `raw_body`, allowing topic/shop header spoofing to redirect a validly-signed payload to another tenant - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`Registry.process` authenticates only `@raw_body` via `Utils::HmacValidator.validate`, then trusts `request.topic` and `request.shop` — both read from unauthenticated HTTP headers — to build the `WebhookMetadata` dispatched to the handler. Any actor holding one legitimately-signed `(raw_body, hmac)` pair (obtainable by installing the app on their own development shop and receiving any webhook) can replay that exact pair to the app's public webhook endpoint while freely setting `x-shopify-topic` and `x-shopify-shop-domain` to arbitrary values, since neither is covered by the signature.

### Finding Description
The broken binding: `(request.topic, request.shop)` acted on by `handler.handle` should equal `(topic, shop)` *authenticated* by the HMAC — but it does not.

- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `@raw_body`/`@headers` are set independently in `initialize` with no cryptographic link between them [2](#0-1) .
- `topic` and `shop` are plain readers over attacker-controlled headers (`x-shopify-topic`, `x-shopify-shop-domain`) [3](#0-2) .
- `HmacValidator.validate_signature` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e. `raw_body`) and compares it to the `hmac` header value; it never touches topic or shop [4](#0-3) .
- `Registry.process` gates only on that body-only HMAC check, then immediately trusts `request.topic` to select the handler and `request.shop` to build `WebhookMetadata` passed to `handler.handle` [5](#0-4) .

Attacker flow: attacker installs the target app on their own development shop, triggers any webhook topic they're entitled to (e.g. `app/uninstalled`), and captures the exact `raw_body` and `x-shopify-hmac-sha256` value Shopify sent to their own registered endpoint. They then issue a direct HTTP POST to the app's public webhook endpoint (the same endpoint code shown in the gem's own docs example wired to `Registry.process` [6](#0-5) ) reusing that identical `raw_body`/HMAC pair, but with `x-shopify-topic: customers/data_request` and `x-shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` recomputes the same HMAC over the same body and secret and succeeds, and `Registry.process` dispatches `handler.handle` with `WebhookMetadata.topic == "customers/data_request"` and `WebhookMetadata.shop == "victim-shop.myshopify.com"`, values the attacker chose and that were never authenticated.

No existing guard closes this gap: `HmacValidator.validate` only checks body integrity [7](#0-6) ; `Request#initialize` only checks header *presence*, not their relationship to the body [8](#0-7) ; `Registry.process` performs no additional shop/topic authentication before dispatch [5](#0-4) .

### Impact Explanation
A handler that trusts `WebhookMetadata.shop`/`topic` (as the gem's documented usage pattern implies it should, since it's the only shop identifier provided) can be made to run mandatory-compliance or data-mutating logic (`customers/data_request`, `customers/redact`, `shop/redact`, `app/uninstalled`, etc.) against a victim shop domain chosen entirely by the attacker, using a body/signature the attacker legitimately possesses for a different topic/shop. This is a cross-tenant authentication-binding failure: the host app is misled into believing an unauthenticated (topic, shop) pair is authenticated. Repeatable against arbitrary victim shop domains and arbitrary registered topics, limited only by which raw_body/hmac pairs the attacker has previously captured from their own legitimate webhook traffic.

### Likelihood Explanation
Preconditions are minimal and attacker-only: create a free development shop, install the target app (a normal, unprivileged action), receive one webhook to capture a valid `raw_body`/`hmac` pair, then send a single forged HTTP POST directly to the app's public webhook endpoint. No secrets, no victim cooperation, and no elevated access are required. The webhook endpoint must be internet-reachable (true by necessity, since Shopify itself delivers webhooks to it over HTTPS).

### Recommendation
Bind topic and shop into the authenticated signable content, or independently authenticate them before use: e.g. require `HmacValidator`/`Request#to_signable_string` to incorporate the topic and shop-domain headers into the signed material to match what the client_secret actually should attest, or have `Registry.process` cross-check `request.shop` against a known/installed-shop store (e.g. via `SessionStorage`) before dispatching to the handler, rejecting shops that have no corresponding active session/installation for the given topic.

### Proof of Concept
Minitest outline (WebMock/Mocha not needed for network, only for computing HMAC directly via `Context.api_secret_key`):
1. Set `ShopifyAPI::Context.setup(api_secret_key: "shhh", ...)`.
2. Compute `hmac = Base64.encode64(OpenSSL::HMAC.digest("sha256", "shhh", raw_body))` for a fixed `raw_body = "{}"`.
3. Register a `FakeWebhookHandler` for topic `"customers/data_request"` via `ShopifyAPI::Webhooks::Registry.add_registration`.
4. Build `headers = { "x-shopify-topic" => "customers/data_request", "x-shopify-hmac-sha256" => hmac, "x-shopify-shop-domain" => "victim-shop.myshopify.com" }` — note the HMAC was computed with no reference to topic or shop.
5. Call `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers))`.
6. Assert no `InvalidWebhookError` is raised (HMAC "passes") and assert the handler received `WebhookMetadata.shop == "victim-shop.myshopify.com"` and `WebhookMetadata.topic == "customers/data_request"`, proving the same `raw_body`/`hmac` pair authenticates arbitrary attacker-chosen topic/shop combinations.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L125-136)
```markdown
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
