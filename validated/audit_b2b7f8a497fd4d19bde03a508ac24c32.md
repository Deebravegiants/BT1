Confirmed: `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) computes the HMAC solely over `verifiable_query.to_signable_string`, and `Request#to_signable_string` returns only `@raw_body` [1](#0-0) . Neither `topic` nor `shop-domain` headers ever enter the signed content [2](#0-1) . `Registry.process` selects the handler purely from `request.topic` after HMAC passes [3](#0-2) , so a body+HMAC pair remains valid under any topic/shop-domain header relabeling.

### Title
`request.topic`/`shop-domain` headers are not covered by the webhook HMAC, allowing handler and tenant relabeling of a validly-signed body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` verifies HMAC exclusively against that string [1](#0-0) [4](#0-3) . Because `Registry.process` dispatches solely on `request.topic` once the HMAC check passes [3](#0-2) , an attacker who obtains one genuine `(raw_body, hmac)` pair signed by the app's shared `client_secret`/`api_secret_key` can relabel the `x-shopify-topic` header (and even `x-shopify-shop-domain`) arbitrarily and have the app's Registry route it to any registered handler while `HmacValidator.validate` still returns true.

### Finding Description
The claimed binding is: `handler_selected_by(request.topic) == handler_authorized_for(HMAC-covered content)`. Tracing the code shows this is **false**: `to_signable_string` = `@raw_body` only [1](#0-0) ; `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from attacker-controllable headers with no cryptographic binding to the body [5](#0-4) . `HmacValidator.validate_signature` recomputes `HMAC(secret, raw_body)` and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header value only — it never touches `topic` or `shop-domain` [4](#0-3) . `Registry.process` then does `@registry[request.topic]&.handler` and hands the parsed body to whatever handler is registered under the attacker-supplied topic string [6](#0-5) .

Critically, the `api_secret_key`/`client_secret` used for HMAC is **app-scoped, not shop-scoped** — it is the same secret for every shop that installs the app. An attacker can install their own app instance on their own development shop, register (via Shopify's normal API, independent of this gem) an additional webhook subscription for any topic pointing to a server they control, and trigger that event to receive one genuine `(raw_body, hmac)` pair signed with the app's real secret. Because the HMAC never covers `topic` or `shop-domain`, the attacker can replay that exact `raw_body` + `hmac` to the app's real webhook-processing endpoint while freely setting `x-shopify-topic` to any registered topic string and `x-shopify-shop-domain` to any value they choose. `HmacValidator.validate` still returns `true` because the body and signature are unchanged, and `Registry.process` will hand the (unrelated) body to whatever handler is registered for the attacker-chosen topic, tagged with an attacker-chosen shop domain in the resulting `WebhookMetadata`.

None of the existing guards prevent this: `HmacValidator.validate` only checks body integrity, not header/topic binding [7](#0-6) ; there is no shop or topic verification anywhere in `Registry.process` [8](#0-7) ; `ShopValidator`/`Context.setup?` are irrelevant here since they aren't invoked in this path.

### Impact Explanation
This is a cross-tenant/authentication-confusion issue at Critical severity: an unprivileged attacker can make the app treat a genuinely-signed webhook body as belonging to an arbitrary shop domain and arbitrary topic, driving it into a handler it was never intended for (e.g., feeding `customers/data_request` body content into an `orders/create` handler, or vice versa), with an attacker-chosen `shop` value passed into `WebhookMetadata`. Any host app that trusts `request.shop`/`request.topic` for authorization, data association, or business logic downstream (which the gem's own `WebhookMetadata` explicitly exposes for that purpose) can be tricked into performing actions against or reporting on a shop the attacker doesn't own. This is repeatable indefinitely and against arbitrary victim shop-domain strings, since the check never validates that the domain in the header actually installed the app or triggered that webhook.

### Likelihood Explanation
The precondition is that the attacker obtains at least one genuine `(raw_body, hmac)` pair from the target app (trivial: install the app on their own dev shop and trigger any webhook-eligible action, or use the mandatory GDPR topics which can be self-triggered). No secrets, tokens, or interception are required — this is header manipulation on a normal HTTP POST to the app's public webhook endpoint. Attacker cost is a single webhook capture plus one crafted replay request; fully repeatable and scriptable.

### Recommendation
Bind `topic` (and ideally `shop-domain`) into the HMAC-covered content, or otherwise cryptographically tie header claims to the signed body — e.g., have `to_signable_string` include topic/shop, or independently verify that the topic/shop declared in headers match values embedded in the signed payload before dispatching in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`). At minimum, log/reject when the same `(raw_body, hmac)` pair is seen with a different topic than previously observed.

### Proof of Concept
Minitest sketch under `test/webhooks/registry_test.rb` style, using WebMock/Mocha to stub `Context.api_secret_key`:
```ruby
raw_body = '{"id":1,"foo":"bar"}'
secret = "shhh"
ShopifyAPI::Context.stubs(:api_secret_key).returns(secret)
hmac = Base64.encode64(OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body))

handler_a = mock("handler_a"); handler_a.expects(:handle).never
handler_b = mock("handler_b"); handler_b.expects(:handle).with(data: anything)

ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", delivery_method: :http, path: "x", handler: handler_a)
ShopifyAPI::Webhooks::Registry.add_registration(topic: "customers/data_request", delivery_method: :http, path: "y", handler: handler_b)

request = ShopifyAPI::Webhooks::Request.new(
  raw_body: raw_body,
  headers: {
    "x-shopify-topic" => "customers/data_request", # attacker-relabeled topic, unrelated to actual body content
    "x-shopify-hmac-sha256" => hmac,                # same hmac, still valid since body unchanged
    "x-shopify-shop-domain" => "victim-shop.myshopify.com",
    "x-shopify-api-version" => "2023-01",
    "x-shopify-webhook-id" => "abc",
  },
)

ShopifyAPI::Webhooks::Registry.process(request)
# assert handler_b.handle was called with body from raw_body, topic "customers/data_request", shop "victim-shop.myshopify.com"
# assert handler_a.handle was NEVER called, proving the same signed content can be redirected to a different handler/tenant purely by header relabeling.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
