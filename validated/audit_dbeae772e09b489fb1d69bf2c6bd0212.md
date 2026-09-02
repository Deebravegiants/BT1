### Title
Webhook `shop-domain` identity is not covered by the HMAC, allowing shop-impersonation on tenant-scoped webhook processing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC computed only over the raw request body, while the `shop` value that identifies *which tenant* the webhook belongs to is read straight from an unauthenticated HTTP header and forwarded to the app's handler unchanged. This mirrors the report's bug class: a field that is *acted on* (the tenant/shop identity) is not part of the data that is *covered by the HMAC* that is verified, so the two can be made to diverge.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (i.e. the body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` unconditionally, passing it into `WebhookMetadata` which is delivered to the app's handler as the tenant identity: [4](#0-3) 

`WebhookMetadata.shop` is documented as "The shop domain of the webhook" and is the field apps are expected to use to scope work to a tenant (e.g. `perform_later(topic: ..., shop_domain: data.shop, ...)`): [5](#0-4) [6](#0-5) 

Equality that should hold but does not:
`HMAC-verified(bytes)` == `bytes used to derive shop identity that is acted on`.

Because the `shop-domain` header sits entirely outside the signed payload, any body that has a valid HMAC for *some* shop (e.g. one an attacker legitimately controls, since anyone can run their own Shopify store and receive real, validly-signed webhooks for it) can be replayed to the app's webhook endpoint with the `shop-domain` header swapped to a different, victim tenant. The gem performs no check that the shop asserted in the header corresponds to the shop whose data was actually signed, and no cross-tenant binding check exists anywhere in `Registry.process`.

### Impact Explanation
This breaks the tenant boundary the whole webhook subsystem is built on. An app author following the documented `WebhookHandler` pattern uses `data.shop` to decide which merchant's records to update (e.g. queue background jobs keyed on `data.shop`, look up per-shop settings/sessions, or write incoming order/customer data under that shop). Since `data.shop` can be forged independently of the HMAC-protected body, an attacker who owns (or has previously received) one valid, signed webhook payload can cause the app to process that payload under an arbitrary victim shop identity — effectively cross-tenant request forgery through the webhook channel. This maps to the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) obtaining any single genuine webhook body+HMAC pair for a shop the attacker controls (trivial — install the app on a free/dev store you own and capture the payload), and (2) POSTing that body to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or `api_secret_key` is needed by the attacker — the HMAC used stays valid because it was never bound to the shop header in the first place. This is fully reachable via the gem's own `Webhooks::Request` / `Webhooks::Registry.process` code path, not dependent on the host app ignoring documented behavior.

### Recommendation
Bind the shop identity into the signed/verified material, or otherwise cryptographically tie `shop-domain` to the request that produced the HMAC:
- Extend `to_signable_string` (or add a secondary check in `Registry.process`) to incorporate `shop`, `topic`, and `webhook_id` alongside the raw body before computing/comparing the HMAC, or
- Require the host application to independently confirm that `data.shop` corresponds to a shop with an active, previously-established session/subscription for that specific `webhook_id`, rejecting anything else, and document this requirement prominently since `WebhookMetadata.shop` is otherwise implicitly trusted by the API surface.

### Proof of Concept
```ruby
# Attacker owns test-shop-a.myshopify.com and receives a real, validly signed
# webhook (any topic) for it, capturing raw_body + headers.

raw_body = '{"id":1,"note":"hello"}'
valid_hmac = "attacker captured valid Shopify HMAC for raw_body signed with the app's api_secret_key"

forged_headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,          # still valid: only signs raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # swapped, unverified
  "x-shopify-webhook-id"  => "any-id",
  "x-shopify-api-version" => "2024-01",
}

# POST raw_body + forged_headers to the app's webhook endpoint.
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds because it only checks raw_body's HMAC.
# The handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# even though that payload was never actually generated for victim-shop.
```

Note: this analysis is based on the indexed contents of `lib/shopify_api/webhooks/*` and `lib/shopify_api/utils/hmac_validator.rb`/`verifiable_query.rb`; no other in-scope binding mismatch (OAuth `AuthQuery`, `JwtPayload`, `SessionUtils`) was found to diverge in the same way — those all keep the identity field (`shop`) inside the signed/verified payload.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
