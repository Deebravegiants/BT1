### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted for tenant dispatch without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by HMAC-verifying the raw request body, but then dispatches and attributes the request using the `shop-domain`, `topic`, and `webhook-id` HTTP headers, none of which are included in the signed payload. This breaks the identity binding `shop_verified_by_hmac == shop_the_app_acts_on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled straight from unauthenticated HTTP headers: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string`, i.e. only over the raw body: [3](#0-2) 

`Registry.process` uses this same HMAC check as the sole authentication gate, then uses the unauthenticated `request.topic` to select the handler and passes the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` straight into `WebhookMetadata`, which the app-level handler treats as the trusted tenant/topic identifier: [4](#0-3) 

The gem's own documentation confirms downstream apps use `data.shop` as the tenant key for further processing (e.g. enqueuing background jobs keyed by shop): [5](#0-4) 

Because `shop-domain` and `topic` sit outside the HMAC-signed content, they can be swapped without invalidating the signature, as long as the raw body itself, and thus the HMAC, stays untouched.

### Impact Explanation
An unprivileged internet user who is themselves a legitimate merchant (i.e. has any shop with the target app installed) can capture one valid raw body + `X-Shopify-Hmac-Sha256` pair from a webhook fired for their own shop, and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop, and/or with `X-Shopify-Topic` rewritten to a different registered topic. `Registry.process` will accept it (the HMAC over the untouched body still validates) and hand the attacker-chosen `shop`/`topic`/`webhook_id`/body to the handler as if Shopify had sent it for the victim shop/topic. Any app that uses `data.shop` to key persistence, authorization, or business logic (exactly as documented) will attribute attacker-controlled webhook content to another tenant — cross-tenant data injection/corruption qualifies as Critical - cross-tenant access.

### Likelihood Explanation
Likelihood is moderate-to-high: the only prerequisite is having any working webhook subscription (any merchant with the app installed can trigger and capture one), and the header manipulation (changing `shop-domain`/`topic` on replay) requires no cryptographic material, since these fields are never part of the signed content.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or equivalent identifying headers) in the HMAC-signable content, or otherwise cryptographically bind them to the request (e.g., have `to_signable_string` concatenate the canonicalized headers with the raw body), so that the whole tenant/topic dispatch decision is protected by the same signature that authenticates the payload.

### Proof of Concept
1. Merchant/attacker owns `attacker-shop.myshopify.com` with the target app installed and subscribed to `orders/create`.
2. Trigger an order event; capture the resulting POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`).
3. Replay the exact same `B`/`H` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` succeeds (only `B` is checked against `H`).
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...))`, and the app processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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
