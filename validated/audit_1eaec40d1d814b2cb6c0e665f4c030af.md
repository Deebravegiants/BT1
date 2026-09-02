This confirms the vulnerability. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which verifies the HMAC only over `request.to_signable_string`, and `Webhooks::Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) . The `shop` field, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the HMAC-covered bytes at all [2](#0-1) . That unauthenticated `shop` value is then passed straight through to the app's handler as `WebhookMetadata#shop` and documented as "The shop domain of the webhook" for the app to act on (e.g., attribute the payload/job to a specific shop/tenant) [3](#0-2) [4](#0-3) [5](#0-4) .

### Title
Webhook `shop` field is trusted by the handler but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body. The `shop` (tenant) identifier is read from an HTTP header that is never included in the HMAC-signed bytes, yet it is handed to the host application's `WebhookHandler` as an authenticated fact about which shop the payload belongs to.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature against `verifiable_query.to_signable_string` [6](#0-5) . For webhooks, `Request#to_signable_string` is defined to return only `@raw_body` [1](#0-0) . Meanwhile `Request#shop` is parsed directly out of the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or the HMAC [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler, and then constructs `WebhookMetadata` using `request.shop` verbatim [4](#0-3) . Because the header is never covered by the signature check, the equality the gem is supposed to guarantee — "the shop the handler is told this webhook is for" == "the shop whose secret actually produced the HMAC over this body" — does not hold. An attacker who possesses one validly-HMAC-signed webhook body/signature pair for shop A (trivial to obtain: they can install the app on their own shop A and receive real webhooks) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming victim shop B. `HmacValidator.validate` still succeeds because it only checks the body bytes, and the handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's real payload>)`.

### Impact Explanation
The documented usage pattern explicitly tells integrators to key off `data.shop` to route/attribute webhook processing per tenant (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [7](#0-6) . Since the gem is the sole component responsible for authenticating webhook requests and asserting their tenant, and it fails to bind `shop` to the HMAC it validates, any host application following the documented contract is exposed to cross-tenant webhook injection — an attacker-controlled shop can inject data that is processed as if it belonged to a different, victim shop/tenant. This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires an unprivileged internet user who can install the target app on any shop they control (or otherwise obtain one legitimately-signed webhook body/HMAC pair) and knowledge of the victim's shop domain (publicly discoverable, e.g., `victim.myshopify.com`). No access to `api_secret_key`, tokens, or the victim's credentials is needed — only a header rewrite on replay.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-verified signable string, or otherwise cryptographically bind `shop` to the validated payload before constructing `WebhookMetadata`, e.g. have `to_signable_string` incorporate `shop`/`topic` alongside `@raw_body`, or perform a secondary check that the `shop` header matches a per-shop secret/session already on file, rejecting the request if it doesn't.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives a legitimate webhook (real hmac computed by Shopify over raw_body):
raw_body = '{"id":1,"note":"hello"}'
real_hmac = Base64.encode64(OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body))

# Attacker replays the same body+hmac but swaps the shop-domain header:
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => real_hmac,          # still valid, since HMAC only covers raw_body
  "shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (body integrity only)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", body: {...}))
# The host app now processes attacker-supplied data as belonging to the victim shop.
```

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

**File:** docs/usage/webhooks.md (L12-30)
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
    end
  end
end
```
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
