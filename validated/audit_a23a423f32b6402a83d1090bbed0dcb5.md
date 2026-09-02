This confirms the finding. The gem explicitly documents that `data.shop` should be trusted by the host app as "The shop domain of the webhook" and used to key work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), yet that field is never covered by the HMAC signature.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header when building the `WebhookMetadata` handed to the app's handler. Because the shop identity is not part of the signed material, a caller that possesses one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` can replay it while substituting an arbitrary `shop-domain` header, causing the handler to process the payload under a different tenant's identity.

### Finding Description
`Registry.process` performs exactly one authenticity check: [1](#0-0) [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the signature only over `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw HTTP body — none of the Shopify-supplied headers are included: [3](#0-2) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from headers and forwarded, unauthenticated, into `WebhookMetadata`, which is the value the host application's handler uses to identify which tenant/shop the event belongs to: [4](#0-3) [1](#0-0) [5](#0-4) 

The gem's own documentation instructs apps to key downstream work off `data.shop`: [6](#0-5) 

This breaks the intended identity binding: `shop_the_hmac_was_computed_for == shop_the_handler_believes_the_event_is_for`. In reality the equality checked by the gem is only `hmac(body) == hmac_header`, with `shop-domain` entirely outside that computation. Any party who legitimately receives even a single valid webhook (e.g., an attacker who installs the app on their own shop, or observes one delivery) obtains a `(body, hmac)` pair that is valid HMAC-wise regardless of which `shop-domain` header accompanies it, because `api_secret_key` is a single app-wide secret shared across all merchants, not shop-specific.

### Impact Explanation
An attacker who can produce or capture one valid `(raw_body, hmac)` pair (trivially achievable by installing the app on their own store and receiving a real webhook, since the signing key is the app-level `client_secret` common to every shop) can replay that exact HTTP request to the app's webhook endpoint while forging the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to name a victim shop. `Registry.process` will accept it as authentic and dispatch the handler with `WebhookMetadata#shop` set to the victim shop, causing the host application to process attacker-controlled webhook content as if it originated from a different merchant. Depending on how the host app uses `data.shop`/`data.body` (e.g., to update per-shop cached data, trigger tenant-scoped jobs, or key lookups), this constitutes cross-tenant data confusion/injection — a boundary crossing between tenants using only the app's own verification logic, matching the "cross-tenant access" impact category.

### Likelihood Explanation
High likelihood: obtaining a valid webhook payload/HMAC pair requires nothing more than being a legitimate (even free/trial) merchant that installs the app, which is available to any unprivileged internet user. No access to `api_secret_key`, access tokens, or TLS interception is required — only observation of one's own genuine webhook delivery and modifying one HTTP header on replay.

### Recommendation
Bind the shop (and ideally topic/webhook_id) identity into the value that is verified, rather than trusting headers outside the HMAC. Options:
- Have `Request#to_signable_string` incorporate the shop-domain (and other trusted headers) in a canonical form covered by the HMAC comparison, or
- After HMAC validation, independently corroborate `shop` against a value obtained through an authenticated channel (e.g., look up the webhook subscription/shop via the API using the app's session rather than trusting the header verbatim), or
- Document/enforce that host applications must not trust `WebhookMetadata#shop` for authorization decisions without additional verification, and add a compensating check (e.g., cross-check shop against the webhook_id via the Admin API) before dispatching to handler.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook (e.g. `orders/create`) and capture the raw request: `raw_body`, and header `x-shopify-hmac-sha256`.
2. Confirm signature validity: `OpenSSL::HMAC.hexdigest("sha256", api_secret_key, raw_body)` matches the captured HMAC (this holds because `api_secret_key` is shared across all shops using the app).
3. Replay the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. Observe `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb#process`) calls `Utils::HmacValidator.validate` which returns `true` (body/HMAC pair is valid), and the handler executes with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker-controlled>)`, despite the request never having been produced by or for `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
