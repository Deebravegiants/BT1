### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then hands the caller-supplied `shopify-shop-domain` header straight through to the app's handler as the tenant identifier. The `shop` field is never covered by the HMAC, so it is not bound to the signature that "authenticates" the request.

### Finding Description
`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [1](#0-0) 

`Utils::HmacValidator.validate` only checks the HMAC against `to_signable_string`, and for `Webhooks::Request` that is defined as just the raw body:
```ruby
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

Meanwhile `shop` is read directly from an HTTP header that is not part of the signed material at all:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

The HMAC is computed with the app's single, global `api_secret_key` — the same secret is valid for every shop that has installed the app [4](#0-3) . This is the same "verified vs. parsed" identity-binding gap as the source report: `HmacValidator.validate` proves the *body* bytes are unmodified and came from someone who knows the app secret, but the code then trusts an unrelated, unsigned `shop` field to decide which tenant the payload belongs to — exactly the "bytes verified versus bytes parsed" / "field acted on but not covered by the HMAC" pattern called out in the rules.

Because any merchant who installs the app is a legitimate holder of valid `(raw_body, hmac)` pairs for their own shop (Shopify delivers real webhooks to them), that merchant — an otherwise unprivileged actor with respect to *other* tenants — can capture one of their own genuine webhook deliveries and replay it to the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a different shop's domain. `HmacValidator.validate` still returns `true` (it only checks the body against the shared secret, which is identical for both shops), and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen shop [5](#0-4) .

### Impact Explanation
Apps built on this gem are documented to key all persistence/business logic off `data.shop` from `WebhookMetadata` (see the documented handler pattern using `data.shop` for job/tenant dispatch) [6](#0-5) . Since this value is trusted without being cryptographically bound to the payload, an attacker can inject data (or trigger data processing/side effects) attributed to a shop they do not control — a cross-tenant confusion/spoofing primitive delivered entirely through this gem's own webhook verification API, not merely a misuse of an undocumented feature.

### Likelihood Explanation
The attacker only needs their own legitimate app installation (any merchant can install a public app) to obtain a valid `(raw_body, hmac)` pair, plus the ability to send an arbitrary HTTP POST to the app's public webhook callback URL with a modified header — no access to `api_secret_key`, tokens, or the target shop's credentials is required. This is a low-effort, directly reachable path through the gem's documented `Registry.process` / `Webhooks::Request` API.

### Recommendation
Bind the shop identity into the verified material, e.g. include `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signable string, or independently verify that the resolved shop has an active, matching session/webhook subscription registered for the specific `webhook_id`/`topic` combination before invoking the handler, so a value not covered by the signature can never override tenant attribution.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and enables an `orders/create` webhook.
2. Shopify delivers a genuine webhook with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker replays the exact same `B` and `H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H` using the (shared) `api_secret_key` [7](#0-6) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim.myshopify.com", ...)`, causing the attacker's order data to be processed/stored as if it belonged to `victim.myshopify.com`.

### Citations

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
