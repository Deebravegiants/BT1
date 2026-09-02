Confirmed: `ShopifyAPI::Webhooks::Request#hmac` is verified only against `to_signable_string`, which returns `@raw_body` alone [1](#0-0) . The `shop`, `topic`, and `webhook_id` values are read straight from unauthenticated HTTP headers [2](#0-1) , and `Registry.process` validates only the HMAC before dispatching the handler and constructing `WebhookMetadata` with `request.shop` and `request.topic` taken directly from those headers [3](#0-2) . This means the identity binding "shop the HMAC authenticates" vs. "shop acted upon by the handler" is broken — the field the host application uses to attribute a webhook to a tenant is never covered by the signature.

### Title
Webhook `shop-domain` (and `topic`) header is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content as only the raw body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from mutable HTTP headers with no cryptographic binding to that signature [2](#0-1) . `Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` and compares it to the `hmac-sha256` header [4](#0-3) . `Registry.process` treats a passing HMAC check as authorization to trust `request.shop` and `request.topic` when building `WebhookMetadata` and dispatching to the app's handler [3](#0-2) .

### Finding Description
Any unprivileged internet user who can install the target app on their own store (or otherwise obtain one legitimate `(raw_body, hmac)` pair produced with the app's shared `client_secret`) can capture that pair and replay it against the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. Because `compute_signature`/`validate_signature` in `HmacValidator` never incorporate the `shop`, `topic`, or `webhook_id` headers into the signed string [5](#0-4) , the signature remains valid for the replayed request regardless of which shop domain is asserted in the header. `Registry.process` performs no additional check that the asserted `shop` actually corresponds to a shop that installed/subscribed to that webhook — it simply forwards `request.shop` into `WebhookMetadata` for the handler to trust [6](#0-5) . This breaks the intended binding: "shop the HMAC authenticates" == "shop the handler is told to act on for".

### Impact Explanation
This is a cross-tenant identity confusion: an attacker-controlled shop's genuine webhook payload can be relabeled as belonging to a victim shop, and the signature will still validate. Any host application that uses `data.shop` from `WebhookMetadata` to select the tenant record to update/delete (the documented and expected usage pattern shown in `docs/usage/webhooks.md`, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be tricked into applying attacker-supplied webhook data under a victim shop's identity — e.g., forging a fake `orders/create`, `app/uninstalled`, or GDPR `shop/redact` event against another merchant. This matches the "cross-tenant access" Critical impact bucket, since the trust boundary between one shop's data and another's is defeated using only the gem's own verification logic.

### Likelihood Explanation
Exploitation only requires the attacker to run the app on a store they control (a normal, unprivileged action for any internet user who can install a public/dev app) to obtain a valid `(body, hmac)` pair, and then send a crafted HTTP request to the app's public webhook endpoint with a forged `shop-domain` header — no access token, `api_secret_key`, or privileged account is needed. This is directly reachable through the gem's documented `Registry.process` entry point.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` headers (not just the body) in the value that is HMAC-verified, or otherwise cryptographically bind the asserted shop domain to the signed payload before trusting `request.shop`/`request.topic` in `Registry.process`. At minimum, document and enforce that host applications must cross-check `request.shop` against a known, previously-authenticated shop/session before acting on webhook data, and consider having `Registry.process` accept an expected-shop allowlist or session lookup to reject webhooks for shops it has no active session for.

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker.myshopify.com"
# and captures one legitimate webhook delivery, e.g. for "orders/create":
raw_body = '{"id":1,"note":"hi"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)

# Attacker replays the same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => SecureRandom.uuid,
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is verified),
#    and the app's handler receives WebhookMetadata with shop: "victim-shop.myshopify.com"
#    even though the request never originated from Shopify for that shop.
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
