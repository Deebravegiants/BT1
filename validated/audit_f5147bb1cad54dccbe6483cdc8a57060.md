Based on the confirmed evidence, this analog is valid: the gem's own documentation states `Registry.process` "will verify the request did indeed come from Shopify" and then dispatches `data.shop` to the handler, but the `shop` claim is never covered by the HMAC.

### Title
Webhook `shop` domain is unauthenticated by HMAC, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` field from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body, not the shop-domain header. This breaks the identity binding `shop verified by HMAC == shop delivered to the app's webhook handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `#shop` is read straight from the mutable `shopify-shop-domain` header without any cryptographic protection: [2](#0-1) 

`Registry.process` validates the request using only `Utils::HmacValidator.validate(request)`, which in turn calls `to_signable_string` (the body only) and compares it against the `hmac` header: [3](#0-2) [4](#0-3) 

After HMAC passes, `request.shop` (attacker-controlled, unauthenticated) is forwarded unmodified into `WebhookMetadata` and handed to the app's registered handler: [5](#0-4) [6](#0-5) 

The gem's own documentation instructs host apps to trust `data.shop` as the identifier of which tenant a webhook body belongs to, and explicitly states that `Registry.process` "will verify the request did indeed come from Shopify": [7](#0-6)  and to use `data.shop` for tenant-scoped work such as enqueuing jobs keyed by `shop_domain`: [8](#0-7) 

Since the HMAC is computed over the body only (with the shared `api_secret_key`, identical for every shop installing the app), any attacker who can obtain one valid `(raw_body, hmac)` pair — e.g., from a webhook delivered to their own shop, or any topic/body they can trigger on a shop they control — can replay that exact body+HMAC while substituting an arbitrary `shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` will still return `true` because it never inspects the shop header, so `Registry.process` accepts the forged request and calls the handler with `WebhookMetadata#shop` set to the victim's domain.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler code, following the gem's documented contract, treats `data.shop` as an authenticated tenant identifier once `Registry.process` succeeds. An attacker can cause the handler to process attacker-supplied webhook bodies as though they originated from any target shop's install, corrupting tenant-scoped state, job queues, or data keyed by shop domain (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)` as shown in the gem's own example). This matches the "cross-tenant access" impact category, since a single app-secret-holding attacker (any shop that installed the app) can forge events attributed to a different, unrelated tenant shop.

### Likelihood Explanation
Likelihood is high for any app author following the documented usage pattern verbatim, since the gem's public API provides no mechanism to bind the shop header to the signature — the interface `Utils::VerifiableQuery` only exposes `hmac` and `to_signable_string` (body-only) [9](#0-8) , and the header-parsing/validation happens entirely inside the gem before the untrusted `shop` value reaches the app. An attacker only needs the ability to trigger one legitimate webhook delivery to a shop they control (any developer/test store) to obtain a valid `(body, hmac)` pair, then can freely relabel the shop header on replay.

### Recommendation
Include the `shop` (and ideally `topic`/`api_version`/`webhook_id`) header values in the HMAC-signed material, or otherwise cryptographically bind the shop-domain header to the signature before trusting `request.shop`/`WebhookMetadata#shop` in `Registry.process`. At minimum, document this gap prominently so host apps do not rely on `data.shop` as an authenticated tenant identifier without additional verification (e.g., cross-checking against a shop for which the app has an active, previously-established session).

### Proof of Concept
```ruby
require "shopify_api"
require "openssl"
require "base64"

ShopifyAPI::Context.setup(
  api_key: "key", api_secret_key: "secret", host_name: "app.example.com",
  scope: [], is_embedded: true, api_version: "2024-01", is_private: false,
)

raw_body = '{"id":123,"note":"legit event from attackers own shop"}'
hmac_digest = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", raw_body)
valid_hmac_b64 = Base64.encode64(hmac_digest) # attacker legitimately obtains this from their own shop's webhook

# Attacker replays the identical body+hmac but swaps the shop-domain header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (only raw_body was checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)) is invoked
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```
