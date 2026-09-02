I have sufficient context to render a verdict.

### Title
Webhook topic is not part of the HMAC signature, allowing topic-relabeling/routing bypass - ([File: lib/shopify_api/utils/hmac_validator.rb], [File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `Registry.process` selects the handler using `request.topic`, a value pulled from the unsigned `x-shopify-topic`/`shopify-topic` header. Because `HmacValidator.validate_signature` never binds the topic to the HMAC, an attacker who obtains one valid `(raw_body, hmac)` pair (e.g. from webhooks Shopify sends to their own installed test shop) can resend it to the app's shared webhook endpoint with the topic header changed, causing the wrong (potentially more sensitive) handler to run against that body.

### Finding Description
The broken binding, stated explicitly: `HMAC(secret, request.to_signable_string) == request.hmac` should imply `request.topic` is authentic, but in fact `to_signable_string` returns only `@raw_body` [1](#0-0) , so the equality that actually holds is only `HMAC(secret, raw_body) == hmac`; `topic` is read straight from an unauthenticated header with no cryptographic tie to the signature [2](#0-1) .

`HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`, never touching topic: [3](#0-2) 

`Registry.process` then validates the HMAC and, independently, uses the same unauthenticated `request.topic` to select and invoke a handler from the registry: [4](#0-3) 

The gem's own documented integration pattern funnels every webhook topic through a single shared controller action that constructs `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` from the raw HTTP request and calls `Registry.process` — dispatch is entirely header-driven, not route-driven: [5](#0-4) 

Exploit flow: the attacker registers/installs the target app on their own development shop and triggers any real webhook event they control (e.g. `app/uninstalled`), receiving from Shopify a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's single, shop-independent `api_secret_key`. The attacker then sends their own HTTP POST directly to the app's shared webhook endpoint, replaying that exact `raw_body` and `hmac`, but overwrites `x-shopify-topic` (and, since it is equally unsigned, `x-shopify-shop-domain`) to name a different, more sensitive registered topic/shop. `HmacValidator.validate` still returns `true` because the signature only ever covered `raw_body`. `Registry.process` then looks up `@registry[request.topic]` for the forged topic and invokes that handler with `WebhookMetadata` built from the attacker-chosen `topic`/`shop` and the replayed body — content the sensitive handler never actually received from Shopify under that topic.

None of the existing guards prevent this: `HmacValidator.validate` only re-runs the same body-only signature check against `api_secret_key` / `old_api_secret_key` [6](#0-5) ; there is no `ShopValidator`, `state`, or JWT check in this webhook path since it is not OAuth/session-token related; `Request#initialize` only checks header *presence*, not any binding between them [7](#0-6) .

### Impact Explanation
An unprivileged attacker (their own shop, no secrets needed) can cause an arbitrary registered webhook handler in the host app to execute against attacker-supplied body content mislabeled as coming from a different, more sensitive topic (and, if the app trusts the `shop` header, an arbitrary shop). This is a topic/shop-scoped authentication bypass: the handler trusts that its input was actually delivered by Shopify for that specific topic, but that binding is not cryptographically enforced. Repeatability is unlimited — any attacker with one genuine webhook from their own shop can replay it indefinitely with any topic label. Blast radius depends on what the mismatched handler does (e.g. a `customers/data_request`/GDPR handler or `shop/update` handler processing unrelated attacker-shaped JSON), which can range from data corruption to privileged-workflow triggering, matching the Critical "authentication bypass" category.

### Likelihood Explanation
Preconditions are low-cost and match documented usage: the app must have a shared webhook endpoint routing purely by header (exactly as shown in `docs/usage/webhooks.md`) and multiple registered topics with distinct handlers. The attacker needs only to install the app on a shop they control and trigger one event to harvest a valid `(raw_body, hmac)` pair — no credentials, no TLS interception, no insider access. This is fully feasible and repeatable.

### Recommendation
Bind the topic (and ideally shop) into the signable string, or otherwise cryptographically/structurally verify that the claimed topic matches the topic Shopify actually signed for — e.g., require topic to be supplied out-of-band per registered endpoint path rather than trusted from the request headers, or include topic/shop in the HMAC computation if Shopify's delivery format supports it. At minimum, document prominently that `request.topic`/`request.shop` are unauthenticated and that apps must register one distinct, topic-specific `path` per webhook and dispatch by route rather than by header before calling `Registry.process`.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (new test)
def test_process_routes_to_wrong_handler_when_topic_header_is_swapped
  body = "{}"
  valid_hmac = Base64.encode64(
    OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
  )

  sensitive_handler_called = false
  sensitive_handler = TestHelpers::FakeWebhookHandler.new(
    lambda { |data| sensitive_handler_called = true }
  )

  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "app/uninstalled", path: "path1", delivery_method: :http,
    handler: TestHelpers::FakeWebhookHandler.new(lambda { |data| }),
  )
  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "customers/data_request", path: "path2", delivery_method: :http,
    handler: sensitive_handler,
  )

  # HMAC was computed for "app/uninstalled" payload, but header claims a different, sensitive topic
  forged_headers = {
    "x-shopify-topic" => "customers/data_request",
    "x-shopify-hmac-sha256" => valid_hmac,
    "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  }

  request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

  ShopifyAPI::Webhooks::Registry.process(request) # does not raise InvalidWebhookError

  assert(sensitive_handler_called, "sensitive handler ran on a body never signed for that topic")
end
```
Both sides of the binding: `computed_signature = HMAC(secret, "{}")` and `received_signature = valid_hmac` match (both computed over the same `raw_body`), yet `request.topic` (`"customers/data_request"`) was never part of that signed string — proving the divergence between "HMAC validity" and "topic authenticity."

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-18)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
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
