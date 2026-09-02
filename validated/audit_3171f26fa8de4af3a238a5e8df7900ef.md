### Title
Webhook `shop` identity passed to handlers is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the `shop` (tenant identifier) exclusively from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Registry.process` validates only covers the raw request body. The `shop` value is never part of the signed bytes, yet it is delivered to the host application's webhook handler as the authenticated tenant identity, breaking the binding `bytes verified == bytes acted on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#hmac` decodes the `hmac-sha256` header for comparison [2](#0-1) . `Request#shop` is read straight from the `shop-domain` header, independent of anything HMAC-covered [3](#0-2) .

`Registry.process` validates the HMAC using `HmacValidator.validate(request)` — which calls `to_signable_string` (body only) — and then, having accepted the request as authentic, forwards `request.shop` unchanged into `WebhookMetadata` handed to the app's handler: [4](#0-3) . `HmacValidator.validate` itself only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` [5](#0-4) , so the check is purely body-vs-hmac, never touching `shop`. `WebhookMetadata.shop` is a plain `String` const with no independent verification [6](#0-5) .

The equality the gem should guarantee is:
`shop_used_by_handler == shop_bound_by_hmac(secret, raw_body)`

but what actually holds is:
`shop_used_by_handler == shop_header (attacker-controlled, unauthenticated)`
`hmac_valid == valid(secret, raw_body)` (independent of `shop`).

Because Shopify's genuine webhook delivery signs only the body per its documented protocol, this is consistent with upstream Shopify's own webhook design (not a defect unique to this gem's cryptography), but the gem still asserts a validated `Request` object and hands `shop` off as if it were part of the verified identity, with no gem-level warning or secondary binding (e.g., cross-checking `shop` against a known/expected tenant or the topic's registered shop) before the host app treats it as authoritative.

### Impact Explanation
If any code path in the host application (or a future misuse of this gem) allows an unprivileged party to replay or synthesize a request with a genuine `hmac-sha256`/body pair (e.g., a webhook they legitimately received for their own low-privilege shop) but a different `shop-domain` header, `Registry.process` will accept it as HMAC-valid and hand the forged `shop` to the app's `WebhookHandler#handle`. Any handler that trusts `data.shop` to select or scope tenant data (a common and Shopify-documented pattern) would then act cross-tenant using a forged shop identity while the request "passes" this gem's own authenticity check — which is exactly the kind of cross-tenant boundary violation this exercise is scoped to catch (Critical: cross-tenant access) if the shop-domain header is attacker-influenced in any deployment/proxy configuration.

### Likelihood Explanation
Medium/Low-High depends entirely on deployment: exploitability requires an attacker to control or spoof the `shop-domain` header value reaching this gem while still supplying a body+hmac pair that the secret validates for a *different* payload/shop, i.e., the attacker needs a valid `(body, hmac)` pair at all (their own tenant's real webhook) and the ability to alter only the header en route (e.g., a proxy/load balancer that doesn't pin headers, or a host framework that reads `shop-domain` from a spoofable source before this gem sees it). This is not exploitable purely against the gem in isolation without such an upstream header-trust gap, so likelihood is bounded by the surrounding integration.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) as part of the value that is cryptographically bound to the HMAC-verified payload, or explicitly document/require that consumers must not treat `Request#shop` as authenticated independent of an out-of-band correlation (e.g., matching it against the shop associated with the session/store that is expected to receive this topic). At minimum, `HmacValidator`/`Request` should not present `shop` as a first-class, seemingly-verified field of an object whose class name and usage pattern imply full authentication of all its accessors.

### Proof of Concept
```ruby
raw_body = '{"id":1}'
secret = ShopifyAPI::Context.api_secret_key
valid_hmac = Base64.encode64(OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body))

# Attacker owns a legit low-privilege shop and received this valid (body, hmac) pair for it,
# then swaps only the shop-domain header before delivering it to the app's webhook endpoint.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by hmac
  "x-shopify-webhook-id" => "abc",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (body matches), handler receives data.shop == "victim-shop.myshopify.com"
```

Note: I could not fully verify whether every real-world transport in front of this gem allows header spoofing while preserving a valid body/hmac pair from a different tenant — that depends on the host application's HTTP stack, which is outside this gem's index. This is flagged as an uncertainty given the ask-only, index-limited scope of this analysis.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L4-12)
```ruby
module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
