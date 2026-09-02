### Title
Webhook `topic` and `shop-domain` headers are not covered by HMAC verification, allowing cross-tenant/cross-topic replay of a single signed body - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` signs and checks solely the body bytes, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. Because those headers are attacker-controlled input to `Request.new(raw_body:, headers:)`, any attacker in possession of one valid `(raw_body, hmac)` pair signed with the app's `api_secret_key` can freely relabel that payload with an arbitrary `shop-domain` and `topic` and have `Registry.process` accept it and dispatch it to a handler as if it belonged to a different shop/topic. The base64url/`decode64` detail in the question is a distractor: `hmac` just re-encodes the attacker-supplied header for comparison and does not itself introduce the unauthenticated-shop problem; the real issue is that the signature never binds to `shop` or `topic` at all.

### Finding Description
The claimed invariant is: `WebhookMetadata#shop` (the value passed to the host app's handler) should equal the shop identity that was cryptographically authenticated by the HMAC check, i.e. `handler_shop == hmac_authenticated_shop`.

Tracing the code:
- `Request#initialize` [1](#0-0)  stores `@headers` and `@raw_body` verbatim from the caller (the host app passes through the raw HTTP headers/body, per the documented usage) [2](#0-1) .
- `Request#shop` returns `shopify_header("shop-domain")` directly, unauthenticated [3](#0-2) .
- `Request#to_signable_string` returns `@raw_body` only [4](#0-3) .
- `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to `verifiable_query.hmac` (the value from the `hmac-sha256` header) via `OpenSSL.secure_compare` [5](#0-4) . The signature is over the body only — `shop`, `topic`, and `webhook_id` never enter the HMAC computation.
- `Registry.process` calls `HmacValidator.validate(request)`, then looks up the handler purely from `request.topic` and builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the same unauthenticated headers, and hands it to the app's `handler.handle(data:)` [6](#0-5) .

Because `api_secret_key` is a single app-wide secret (not per-shop), any attacker who installs the app on their own shop and receives one legitimately-signed webhook obtains a `(raw_body, hmac)` pair that is valid for that same `api_secret_key` regardless of which shop or topic label is attached to it. The attacker can then submit that same body+hmac to the app's webhook endpoint with `X-Shopify-Shop-Domain` set to a victim's shop and `X-Shopify-Topic` set to any registered topic (e.g. `customers/redact` or `shop/redact`, or any topic whose handler acts on `data.shop`); `HmacValidator.validate` still passes since it only checks the body, and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` claiming to be the victim shop. No existing guard (`ShopValidator.sanitize!`, `Context.setup?`, Sorbet typing) checks that the `shop`/`topic` headers are bound to the signature — Sorbet only enforces types, not authentication, and there is no `ShopValidator` call anywhere in this webhook path.

### Impact Explanation
This breaks the "single identity per request" invariant: `shop` used for authorization/dispatch decisions is not the same value that was cryptographically verified (the verification covers only the body). A host app that — per the documented usage pattern — trusts `WebhookMetadata#shop` and `WebhookMetadata#topic` to decide "whose records to touch" (e.g., queue a job scoped to `data.shop`, or run GDPR redaction for `data.shop`) can be made to act on an attacker-chosen shop and topic using a signed body harvested from the attacker's own (legitimately owned) shop. This is a cross-tenant integrity issue: one tenant's signed traffic can be relabeled to affect another tenant's data/processing. It does not directly expose or steal an Admin API access token or `client_secret` by itself — the finding in `request.rb`/`registry.rb` does not create a path to token theft; that portion of the question's "Critical - theft of a merchant's Admin API access token" framing is not substantiated by the code reachable from this bug. The realistic mapped impact is cross-tenant data manipulation (closer to the "cross-tenant access" Critical class) contingent entirely on what the host app's handler does with `data.shop`/`data.topic`, which is outside this gem's control.

### Likelihood Explanation
Preconditions: attacker needs a working relationship with the app (install on their own dev shop, as explicitly permitted in the threat model) to obtain one legitimately signed webhook body+hmac pair, and the target app must (a) register at least one topic handler and (b) use `data.shop`/`data.topic` for tenant-scoped side effects without independently re-verifying shop ownership (e.g., without cross-checking against a known/authorized session for that shop). Both are normal, gem-documented usage patterns. Attacker cost is low (they already legitimately receive webhooks); the replay is fully repeatable against arbitrary shop-domain strings and arbitrary registered topics, since neither is bound to the signature.

### Recommendation
Bind `shop-domain`, `topic`, and ideally `webhook-id`/`api-version` into the signable content, or otherwise validate them out-of-band (e.g. reject the request if `shop` does not correspond to a shop with an active `Auth::Session`/registration known to the host app for the topic in question) before constructing `WebhookMetadata`. At minimum, document explicitly that only `raw_body` is HMAC-verified and that host apps must not treat `data.shop`/`data.topic` as authenticated identifiers without an additional application-level check.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (additional test)
def test_replayed_body_with_forged_shop_and_topic_is_accepted
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)

  handler_a = FakeWebhookHandler.new
  handler_b = FakeWebhookHandler.new
  ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", delivery_method: :http,
    handler: handler_a, path: "cb/a")
  ShopifyAPI::Webhooks::Registry.add_registration(topic: "customers/update", delivery_method: :http,
    handler: handler_b, path: "cb/b")

  body = '{"id": 1}'
  hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", body)
  hmac_b64 = Base64.strict_encode64(hmac)

  # Legit request as attacker's own shop, topic "orders/create"
  legit_headers = {
    "x-shopify-hmac-sha256" => hmac_b64,
    "x-shopify-topic" => "orders/create",
    "x-shopify-shop-domain" => "attacker.myshopify.com",
    "x-shopify-webhook-id" => "1",
    "x-shopify-api-version" => "2023-01",
  }
  ShopifyAPI::Webhooks::Registry.process(
    ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: legit_headers)
  )
  assert_equal "attacker.myshopify.com", handler_a.last_data.shop

  # Replay SAME body+hmac, forged shop + topic -> should be rejected but is accepted
  forged_headers = legit_headers.merge(
    "x-shopify-topic" => "customers/update",
    "x-shopify-shop-domain" => "victim.myshopify.com",
  )
  ShopifyAPI::Webhooks::Registry.process(
    ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
  )
  # Demonstrates unauthenticated shop/topic reached handler_b as "victim.myshopify.com"
  assert_equal "victim.myshopify.com", handler_b.last_data.shop
end
```
This demonstrates that the HMAC check passes and the handler receives a `WebhookMetadata#shop`/`topic` combination that was never covered by the signature — confirming the identity used for dispatch is not the identity that was authenticated. Note: the base64url `-`/`_` `decode64` detail described in the question does not independently contribute to this bug; it was not needed to construct the PoC above.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L127-135)
```markdown
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
