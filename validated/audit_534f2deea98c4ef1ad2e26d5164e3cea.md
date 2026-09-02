### Title
Webhook signature covers only the raw body, allowing topic/shop header forgery to be accepted as authentic - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` never covers `request.topic`, `request.shop`, `request.webhook_id`, or `request.api_version`. An attacker who legitimately receives one genuinely Shopify-signed webhook (e.g., by installing the app on their own development shop) can replay that same body/HMAC pair while swapping the unsigned `X-Shopify-Topic` and `X-Shopify-Shop-Domain` headers, and `Registry.process` will still treat it as authentic.

### Finding Description
The broken binding is:
`computed_hmac(request.raw_body) == received_hmac` is treated as equivalent to `authentic(request.topic, request.shop, request.raw_body)`, but these are not equal because only `request.raw_body` is inside the signed content.

Trace:
- `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) does exactly one authentication check: `Utils::HmacValidator.validate(request)`, then immediately trusts `request.topic` for handler dispatch and `request.shop` for tenant attribution when building `WebhookMetadata`. [1](#0-0) 
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header via `OpenSSL.secure_compare`. [2](#0-1) 
- `Request#to_signable_string` returns only `@raw_body` — `topic`, `shop`, `webhook_id`, and `api_version` are all read from headers (`shopify_header`) and are never mixed into the signable string. [3](#0-2) 

There is no delivery-id, timestamp, or nonce bookkeeping anywhere in `registry.rb` or `hmac_validator.rb` to bound re-delivery or bind the signature to a specific topic/shop/delivery event — confirmed by reading both files in full.

Exploit flow (within the rules' allowed attacker capability of "create own dev shop, install app, receive own validly signed webhooks, control headers"):
1. Attacker installs the target app on their own dev shop and subscribes to some topic (e.g., `orders/create`). Shopify sends a genuinely signed webhook: raw body `B`, `X-Shopify-Hmac-Sha256: H` computed with the app's real `client_secret` over `B`.
2. Attacker replays a POST to the same app's public webhook endpoint, keeping body `B` and header `H` unchanged, but sets `X-Shopify-Topic` to a different registered topic (e.g., `customers/redact`, which many apps register a local handler for even though Shopify manages its subscription) and/or `X-Shopify-Shop-Domain` to an arbitrary victim shop's `.myshopify.com` domain.
3. `HmacValidator.validate` recomputes the signature over `to_signable_string` (= `B`) and it still matches `H`, so `process` does not raise `Errors::InvalidWebhookError`.
4. `Registry.process` looks up the handler using the forged `request.topic`, then invokes `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` — the handler executes believing it received an authentic delivery for the forged topic/shop. [4](#0-3) 

None of the existing guards prevent this: `ShopValidator.sanitize!`, `JwtPayload`'s `aud` check, and `HttpRequest#verify` are used in OAuth/session-token flows, not in the webhook `Request`/`Registry` path, and `Context.setup?`/`private?`/`embedded?` play no role in webhook signature validation.

### Impact Explanation
An attacker can make the app's registered webhook handler(s) execute with a forged topic and/or a forged shop domain while still passing signature validation, because the shop/topic metadata acted upon downstream is not covered by the HMAC. This can misattribute an action to another tenant (`request.shop` forged to a victim's domain) or trigger a mismatched handler (topic confusion, e.g., feeding an `orders/create` body into a `customers/redact` handler). This is repeatable against arbitrary victim shop domains (which are public, guessable `.myshopify.com` subdomains) for as long as the attacker holds one validly-signed body from any topic they have access to. This maps to "cross-tenant access" / "authentication bypass" impact, since a request whose claimed topic/shop is forged is nonetheless accepted by `process` as authentic.

### Likelihood Explanation
Preconditions are minimal and entirely within the defined attacker capability: create a development shop, install the target app, and receive at least one real webhook delivery. No credentials, secrets, or victim cooperation are needed. Cost is a single legitimate webhook subscription plus standard HTTP tooling to replay/modify headers. This is straightforward and fully repeatable.

### Recommendation
Include `topic`, `shop-domain`, and (ideally) `webhook-id`/timestamp in the signed content bound to the delivery, or otherwise cryptographically bind the header values used for dispatch/tenant-attribution to the HMAC-validated payload, e.g. by having `to_signable_string` incorporate a canonicalized representation of the headers actually acted upon, and/or track `webhook_id` to reject replays across topics/shops.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (new test)
def test_process_dispatches_by_forged_topic_header_despite_valid_body_hmac
  raw_body = '{"id":1}'
  secret = ShopifyAPI::Context.api_secret_key
  hmac = Base64.strict_encode64(
    OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
  )

  handler_a = mock
  handler_a.expects(:handle).never
  handler_b = mock
  handler_b.expects(:handle).once

  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "orders/create", delivery_method: :http, path: "/a", handler: handler_a,
  )
  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "customers/redact", delivery_method: :http, path: "/b", handler: handler_b,
  )

  request = ShopifyAPI::Webhooks::Request.new(
    raw_body: raw_body,
    headers: {
      "X-Shopify-Topic" => "customers/redact",       # forged, unsigned
      "X-Shopify-Shop-Domain" => "victim-shop.myshopify.com", # forged, unsigned
      "X-Shopify-Hmac-Sha256" => hmac,                # valid only for raw_body
      "X-Shopify-Webhook-Id" => "whatever",
      "X-Shopify-Api-Version" => "2023-01",
    },
  )

  # Assert HmacValidator accepts it despite forged topic/shop
  assert ShopifyAPI::Utils::HmacValidator.validate(request)

  # Assert process dispatches based on forged topic, proving topic/shop
  # are outside the signed content (to_signable_string == raw_body only)
  ShopifyAPI::Webhooks::Registry.process(request)
end
```
Both sides of the equality diverge: `computed_hmac(raw_body) == received_hmac` holds true, while `request.topic`/`request.shop` (acted upon in `handler.handle`) are attacker-controlled and unauthenticated — confirming the SIGNATURE COVERAGE invariant is violated.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
