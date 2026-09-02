### Title
Webhook `shop` and `topic` identity are not bound by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC against the body only and then dispatches to the app's handler using the unauthenticated `shop`/`topic` header values as the tenant/event identity. This breaks the intended binding `authenticated(body) == trusted(shop, topic)`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `shop`/`topic` are pulled straight from headers with no involvement in the signature: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC: [3](#0-2) 

`Registry.process` treats a valid body HMAC as sufficient proof of the whole request, then forwards the unauthenticated `request.shop` and `request.topic` to the app's handler as the trusted tenant/event context: [4](#0-3) 

The documented integration pattern explicitly uses `data.shop` as the tenant key for downstream processing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), so the gem's own guidance encourages using this unauthenticated field to select tenant state: [5](#0-4) 

**Equality that should hold but doesn't:** `hmac_verified(shop_header) == hmac_verified(raw_body)`. In reality only `raw_body` is bound to the signature; `shop_header` (and `topic_header`) can be changed to any value after a legitimately-signed body is obtained, and the HMAC still validates.

**Attack path:** the app's `client_secret` (`Context.api_secret_key`) is shared across every merchant install of the app. An attacker who is any unprivileged merchant that installs the target public app can:
1. Trigger a legitimate webhook delivery to their own endpoint for a topic where the body content they control is embedded (e.g. `products/update` with attacker-chosen title/tags/notes fields), obtaining a `(raw_body, hmac)` pair that Shopify signed with the app's real `client_secret`.
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but swap the `x-shopify-shop-domain` header to a victim shop's domain and/or the `x-shopify-topic` header to any registered topic.
3. `HmacValidator.validate` still passes because the signature only covers `raw_body`, and `Registry.process` calls the app's handler with `shop: <victim shop>`.

### Impact Explanation
This allows cross-tenant event injection/spoofing: an attacker-controlled body is delivered to the app's handler while all header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) are fully attacker-controlled and disconnected from the signature. Any host app that keys per-tenant state, job queues, or data updates off `data.shop` (as the gem's own documentation recommends) can have data attributed to or acted upon for a shop the attacker does not control, i.e. cross-tenant access.

### Likelihood Explanation
Requires only an unprivileged merchant account/installation of the target public app — no leaked secrets, no privileged access, and no host-application misuse beyond following the gem's documented `data.shop`/`data.topic` usage pattern.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the signable string (or otherwise cryptographically tie them to the signed payload) so that `HmacValidator.validate` fails if any of these header-derived values are altered, mirroring how `AuthQuery#to_signable_string` includes `shop` in its signed parameters (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`).

### Proof of Concept
1. As merchant A (attacker), install the target app and receive a real webhook, e.g. `products/update`, capturing headers `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain: shop-a.myshopify.com`, and the raw JSON body containing attacker-chosen field values.
2. POST the identical raw body and `x-shopify-hmac-sha256` value to the same app webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) passes HMAC validation (body unchanged) and invokes the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, confirming the identity binding break.

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
