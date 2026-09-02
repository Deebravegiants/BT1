### Title
Webhook HMAC signs only the raw body while shop/topic identity headers are trusted unsigned - cross-tenant webhook spoofing (`lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`HmacValidator.validate_signature` computes and compares the HMAC only over `verifiable_query.to_signable_string`, and for webhooks that string is exactly `@raw_body` [1](#0-0)  and [2](#0-1) . The `shop-domain` and `topic` values that `Webhooks::Registry.process` trusts to select a handler and attribute data to a shop [3](#0-2)  come from HTTP headers that are never included in the signed bytes [4](#0-3) , so an attacker who legitimately receives one webhook for their own shop (signed with the app-wide `api_secret_key`) can replay the same body+HMAC to the app's public webhook endpoint with a forged `shop-domain`/`topic` header and pass validation.

### Finding Description
The claimed binding is: `bytes signed by compute_signature(verifiable_query.to_signable_string, secret)` == `bytes later parsed and acted on by the webhook handler (topic + shop + body)`.

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors all read directly from HTTP headers that are not part of that signable string [5](#0-4) . `HmacValidator.validate_signature` only ever hashes `to_signable_string` and compares against the `hmac` header via `OpenSSL.secure_compare` [2](#0-1) ; it never touches `shop`, `topic`, or any other header. `Webhooks::Registry.process` then trusts `request.shop` and `request.topic` — unauthenticated header values — to route to a handler and populate `WebhookMetadata` [3](#0-2) .

Because `api_secret_key` is one value shared by every shop that installs the app (not per-shop), an attacker who installs the app on their own development shop receives a genuinely-signed webhook (`raw_body` + valid `hmac`). The webhook endpoint is a public HTTP endpoint (that's the entire reason HMAC validation exists), so the attacker can POST that exact `raw_body`+`hmac` pair directly to the victim app's webhook URL while setting arbitrary `X-Shopify-Shop-Domain` and `X-Shopify-Topic` headers. `validate_signature` still succeeds because the signature never covered those headers, and `Registry.process` dispatches the (attacker-supplied) body to whatever handler the forged topic selects, tagging it with whatever shop the forged header claims — a byte-identity divergence between what was signed and what is acted on.

The `old_api_secret_key`-never-expires detail widens the window (a rotated secret remains valid forever) but is not itself the root cause; the root cause is that the signed byte range excludes the header fields the rest of the pipeline treats as authenticated. Existing guards (`ShopValidator.sanitize!`, `state` comparisons, JWT `aud` checks) do not apply here — those protect the OAuth/session-token paths, where `AuthQuery#to_signable_string` does include `shop` in the signed parameters [6](#0-5) , so OAuth callbacks are not vulnerable to this specific header/body divergence. Only the webhook path is affected.

### Impact Explanation
An attacker can get an app built on this gem to process a forged webhook as if it originated from an arbitrary victim shop and/or trigger an arbitrary registered topic handler with attacker-chosen JSON content, because `request.shop` and `request.topic` are unauthenticated relative to the HMAC. Depending on what the host app's `WebhookHandler` implementations do with `WebhookMetadata#shop` (e.g. looking up that shop's session/access token and performing a mutation), this can lead to reading or mutating another merchant's data — matching "Critical - cross-tenant access." This is repeatable indefinitely and against arbitrary victim shop domains, since the attacker only needs one valid `raw_body`/`hmac` pair from their own tenancy and can reuse it with different forged headers each time.

### Likelihood Explanation
Preconditions: the app must use `ShopifyAPI::Webhooks::Registry.process` to validate and dispatch webhooks (the gem's documented pattern) and must act on `WebhookMetadata#shop`/`#topic` without independently re-validating shop identity. The attacker only needs to install the app on a development shop they control (free, self-service) to obtain one legitimately signed webhook payload; they need no secret, token, or victim cooperation. This is low-cost and fully attacker-controlled.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used by `HmacValidator`, or independently authenticate the shop domain (e.g., cross-check `request.shop` against session/shop records established via OAuth, and reject if it doesn't match a known installed shop) before dispatching to handlers in `Webhooks::Registry.process`. Also consider adding an expiry/cutover mechanism for `old_api_secret_key` so rotated secrets stop being accepted after a bounded grace period.

### Proof of Concept
```ruby
# test/webhooks/cross_tenant_replay_test.rb
require "test_helper"

class CrossTenantReplayTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host_name: "host",
      scope: "scope", is_embedded: false, api_version: "unstable",
      is_private: false,
    )
  end

  def test_body_hmac_ignores_shop_and_topic_headers
    raw_body = '{"id":1}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", raw_body),
    )

    # Payload legitimately obtained for attacker's own shop
    attacker_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-hmac-sha256" => hmac,
        "x-shopify-topic" => "orders/create",
        "x-shopify-shop-domain" => "attacker.myshopify.com",
        "x-shopify-api-version" => "unstable",
        "x-shopify-webhook-id" => "1",
      },
    )
    assert ShopifyAPI::Utils::HmacValidator.validate(attacker_request)

    # Same raw_body + hmac replayed with victim shop / different topic header
    forged_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-hmac-sha256" => hmac,
        "x-shopify-topic" => "customers/redact",
        "x-shopify-shop-domain" => "victim.myshopify.com",
        "x-shopify-api-version" => "unstable",
        "x-shopify-webhook-id" => "2",
      },
    )
    # BYTE IDENTITY BROKEN: same signature validates a request now
    # attributed to a different shop and a different topic.
    assert ShopifyAPI::Utils::HmacValidator.validate(forged_request)
    assert_equal "victim.myshopify.com", forged_request.shop
    assert_equal "customers/redact", forged_request.topic
  end
end
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
