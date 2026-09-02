### Title
`Webhooks::Registry.process` dispatches and attributes webhooks using `topic`/`shop-domain` headers that are excluded from `to_signable_string`, allowing signed-body replay under forged headers - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only signs and checks `Request#to_signable_string`, i.e. the raw body. It then uses `request.topic` and `request.shop` — read straight from attacker-controlled HTTP headers — to select the handler and to populate `WebhookMetadata` passed to app code. Since the signature never covers `topic`/`shop-domain`/`webhook-id`/`api-version`, an attacker who possesses one validly-signed `(raw_body, hmac)` pair (trivially obtainable by installing the app on their own dev store and receiving a real webhook) can resend that exact body with a different `topic` or `shop-domain` header and still pass `HmacValidator.validate`, causing the app to dispatch to a different handler or attribute the payload to a different shop than what was actually signed.

The specific claim in the question about `add_registration`/`clear` racing on `@registry` is not supported: those methods are invoked only by the app's own developer code (registration setup), never by the public `process` entrypoint, so an unprivileged HTTP attacker has no path to mutate `@registry` concurrently with `process`. That part of the premise is invalid. However, tracing the actual "SIGNATURE COVERAGE" invariant named in the question does reveal a real violation via the header/topic vector, matching the question's own suggested fast-validation test.

### Finding Description
The invariant that should hold: `handler_dispatched_for(request) == handler_registered_for(topic_that_was_actually_signed)`. In practice:

- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) .
- `Request#topic`, `#shop`, `#webhook_id`, `#api_version` are all read directly from HTTP headers with no HMAC coverage [2](#0-1) .
- `Registry.process` validates only the signable string, then uses the unsigned `request.topic` to look up the handler and unsigned `request.shop` to build `WebhookMetadata` handed to the app: [3](#0-2) .
- `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` only, and never mixes in topic/shop: [4](#0-3) .

Attack: an attacker installs the target app on their own development shop (a permitted action) and receives one genuinely-signed webhook — a real `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's real secret. They then send an HTTP POST directly to the app's public webhook route with that identical body/hmac but with `x-shopify-topic` and/or `x-shopify-shop-domain` headers changed to values of their choosing. `HmacValidator.validate` still returns `true` because it only re-hashes the untouched raw body. `Registry.process` then dispatches using the forged `topic` header to whatever handler is registered for that topic, and constructs `WebhookMetadata` carrying the forged `shop` value into app handler code that never re-verified it.

Existing guards do not prevent this: `HmacValidator.validate` checks only what `to_signable_string` includes, `ShopValidator`/`JwtPayload` are unrelated to this code path, and there is no per-request binding of topic/shop into the signed material.

### Impact Explanation
This is a data-integrity / authentication bypass at the boundary the app relies on for tenant and event-type attribution: a request whose body was never signed for "topic X" or "shop Y" is delivered to the handler for topic X and/or tagged as coming from shop Y. If a host app's handler trusts `WebhookMetadata#shop` for tenant scoping (a common and documented usage pattern), an attacker with control of only their own dev-store webhook can inject data attributed to an arbitrary `shop` domain string, or trigger a handler for a topic whose payload shape it was never built to expect (e.g., feeding a `shop/redact`-shaped body into a topic-specific handler). This is repeatable at will against any handler the app has registered and does not require compromising Shopify's secret.

### Likelihood Explanation
Preconditions: the attacker needs one legitimately-signed webhook body from their own shop (trivial — install the app, generate an event) and the ability to send arbitrary HTTP requests with arbitrary headers directly to the app's public webhook endpoint (given, per the threat model). No credentials, no timing race, and no access to `api_secret_key` are needed. Feasibility is high and the exploit is fully repeatable.

### Recommendation
Include the values used for routing/attribution in the signed material, or independently verify them: at minimum, `Registry.process` should require that `request.shop` matches a session/shop already known to be legitimate for the topic being processed, and/or the app's webhook signature scheme should be extended so that `topic`, `shop-domain`, and `webhook-id` headers are covered by the HMAC (not just the body), rejecting any request where header values were altered relative to what Shopify actually sent.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb
def test_process_dispatches_by_unsigned_topic_header_not_by_signature
  body = "{}"
  hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
  hmac_b64 = Base64.encode64(hmac)

  handler_a_called = false
  handler_b_called = false

  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "topic/a", delivery_method: :http, path: "path",
    handler: TestWebhookHandler.new(->(*) { handler_a_called = true }),
  )
  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "topic/b", delivery_method: :http, path: "path",
    handler: TestWebhookHandler.new(->(*) { handler_b_called = true }),
  )

  # Attacker took a validly-signed (body, hmac) pair issued for "topic/a"
  # and resent it with the topic header swapped to "topic/b".
  forged_headers = {
    "x-shopify-topic" => "topic/b",       # unsigned, attacker-controlled
    "x-shopify-hmac-sha256" => hmac_b64,  # signature only covers body
    "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  }

  ShopifyAPI::Webhooks::Registry.process(
    ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers),
  )

  # Assert dispatch followed the *signature* (i.e. should have gone to handler_a,
  # since the signed body was originally issued for topic/a), not the header.
  refute(handler_b_called, "handler for forged topic/b ran despite signature never covering topic")
  assert(handler_a_called, "handler for the actually-signed topic/a should have run")
end
```
This demonstrates that `HmacValidator.validate` passes despite the `topic` (and equally `shop-domain`) header being changed post-signing, because `Request#to_signable_string` at [1](#0-0)  never includes them, confirming the signature-coverage violation named in the invariant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
