This confirms the vulnerability. `Webhooks::Request#to_signable_string` returns only `@raw_body` (the JSON body), while `Request#shop` and `#topic` are read directly from HTTP headers with no cryptographic binding to the HMAC signature.This confirms the finding is well supported: `Webhooks::Request#shop` (and `#topic`, `#webhook_id`, `#api_version`) are read straight from HTTP headers with no cryptographic tie to the HMAC, since `to_signable_string` (line 36-38) returns only `@raw_body`. This is the exact analog class called out in the rules ("a field acted on but not covered by the HMAC").

### Title
Webhook `shop` (and `topic`) header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `api_version`, and `webhook_id` values purely from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.), while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. This breaks the intended identity binding `hmac == HMAC(shop || topic || body)`; in reality it enforces only `hmac == HMAC(body)`, leaving `shop` and `topic` completely unauthenticated.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `#shop` and `#topic` are read directly from attacker-visible/attacker-settable HTTP headers with no cryptographic binding to that signature: [2](#0-1) 

`Webhooks::Registry.process` validates the HMAC against the body only, then dispatches the handler using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, which explicitly includes `shop` (and `host`, `code`, `state`, `timestamp`) in the signed string, correctly binding the shop identity to the HMAC in the OAuth callback flow: [4](#0-3) 

The webhook path lacks this same protection. Since the HMAC only proves the body's integrity/authenticity, any request with a body+HMAC pair that is valid for the shared `client_secret` (e.g., any webhook a merchant legitimately receives at their own publicly-reachable endpoint, since Shopify signs bodies with the app's single `client_secret` shared across all installs) can be replayed to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header substituted in. The gem will accept it as valid and hand `WebhookMetadata` down to the app's handler with the attacker-chosen `shop` value: [5](#0-4) 

The documented handler contract explicitly tells app developers to trust `data.shop` as the shop domain of the webhook, encouraging code that keys storage/state updates off this unauthenticated value: [6](#0-5) 

### Impact Explanation
This allows a merchant who has installed the app (and therefore can legitimately trigger and capture at least one genuinely-signed webhook body+HMAC pair, since the same `client_secret` signs webhooks for every shop on the app) to relabel that payload as belonging to any other victim shop domain by simply setting a different `x-shopify-shop-domain` header value on a replayed request to the app's public webhook endpoint. Because `Webhooks::Registry.process` and `WebhookMetadata` never re-validate that the header-derived `shop` matches anything cryptographically tied to the signed body, downstream app logic that uses `data.shop` to select which tenant's data/session to update (as instructed by the gem's own documentation) can be tricked into applying attacker-supplied webhook data to a different tenant's records — a cross-tenant data-integrity violation.

### Likelihood Explanation
Requires only: (1) legitimate app installation on any one shop to obtain a validly-signed webhook body/HMAC pair (which merchants can do without any special privilege), and (2) the ability to send a direct, unauthenticated HTTP POST to the app's public webhook callback URL with a modified `shop-domain` header — webhook endpoints are internet-reachable by design and require no additional secret to reach. No `client_secret`, access token, or TLS interception is required by the attacker.

### Recommendation
Bind `shop` (and ideally `topic`) into the HMAC-signed material, e.g. by having `to_signable_string` incorporate the header values that are trusted downstream, or by independently verifying that the shop domain in the header matches an expected/registered value before dispatching to handlers. At minimum, document (and ideally enforce) that `WebhookMetadata#shop` must not be trusted as authenticated identity unless the app performs its own additional verification.

### Proof of Concept
1. App merchant `attacker.myshopify.com` installs the app and lets Shopify deliver a legitimate webhook (e.g. `orders/create`) to the app's public HTTP endpoint; the merchant captures the raw request, including `x-shopify-hmac-sha256` and body `{"id":1}`.
2. Attacker replays the exact same body and HMAC header to the same endpoint but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Webhooks::Request#hmac` returns the same HMAC value; `Utils::HmacValidator.validate` recomputes `HMAC(body)` with the shared `client_secret` and it matches, per: [7](#0-6) 
4. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, even though the actual signed webhook body originated from, and was intended for, `attacker.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
