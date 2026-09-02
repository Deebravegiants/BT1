### Title
Webhook `shop`/`topic`/`webhook_id` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, and `ShopifyAPI::Webhooks::Registry.process` only verifies that body against the HMAC header. The `shop`, `topic`, `webhook_id`, and `api_version` values — read straight from unauthenticated HTTP headers — are handed to the app's webhook handler as trusted tenant-identifying data, even though none of them are covered by the signature.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. The `shop`, `topic`, `webhook_id` and `api_version` accessors read directly from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`HmacValidator.validate` computes the signature only from `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this validation result as the sole authenticity check, and then forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` straight to the app's handler as trusted identifiers: [4](#0-3) 

The equality this breaks is: **shop that the HMAC actually authenticates (the raw body content signed with the app's shared secret) ≠ shop that the handler is told the webhook belongs to (`x-shopify-shop-domain` header, unauthenticated)**. Any HTTP header supplied to the webhook endpoint can be freely set by whoever is sending the POST, so `request.shop`/`request.topic`/`request.webhook_id` carry no integrity guarantee at all — only the byte content of the body is verified.

The gem's own documentation instructs developers to trust `data.shop` as "The shop domain of the webhook" and shows it being passed straight into application logic (`shop_domain: data.shop`) without any caveat that it is unauthenticated: [5](#0-4) 

### Impact Explanation
An app that follows this gem's documented pattern (using `data.shop` from `WebhookMetadata` to select which merchant's records to update) can be made to apply a webhook payload to the wrong tenant. Since the app's webhook shared secret (`api_secret_key`) is the same across every shop that installs the app, any store that has installed the app receives legitimately HMAC-signed webhook bodies. Whoever controls that store (or intercepts the raw body/HMAC pair some other way) can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header for an arbitrary victim shop. `Registry.process` will still consider the request valid (the HMAC check only covers the body) and will dispatch it to the handler labeled as belonging to the victim shop, causing cross-tenant data confusion/corruption — e.g. writing another merchant's order/webhook payload into the attacker-chosen shop's records, or bypassing per-shop authorization checks that key off `data.shop`.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint plus one legitimately signed webhook body (trivially obtainable by installing the target app on any store, which is normal for a public/embedded Shopify app). No access to `api_secret_key`, access tokens, or privileged credentials is required — this is exactly the "unprivileged internet user" scenario in scope. The vulnerable pattern is exactly what the gem's own documentation recommends developers do.

### Recommendation
- Do not treat header-derived `shop`, `topic`, `webhook_id`, or `api_version` as authenticated identifiers unless bound into the signed payload.
- Include these values in the HMAC-signable representation (or require verifying the tuple `(shop, webhook_id)` against an app-side registry of webhooks actually registered for that shop) before dispatching to the handler.
- At minimum, update the documentation to explicitly warn that `data.shop`/`data.topic`/`data.webhook_id` are not covered by HMAC verification and must be independently corroborated (e.g., checked against the shop associated with the session/webhook registration) before being used for tenant-scoped operations.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`. Shopify sends a legitimately-signed webhook, e.g.:
   ```
   POST /webhook
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of BODY signed with the app's shared secret>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: <id>
   Body: BODY
   ```
2. Attacker captures `BODY` and the valid `x-shopify-hmac-sha256` value.
3. Attacker resends the exact same request to the app's public webhook endpoint, but changes the header:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
   (topic/webhook_id could likewise be altered.)
4. `ShopifyAPI::Webhooks::Request.new(raw_body: BODY, headers: headers)` is constructed by the app, and `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `BODY` — it never inspects `shop`/`topic`/`webhook_id`.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: ..., ...)`, causing the app to process attacker-supplied `BODY` as though it belongs to `victim.myshopify.com`.

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
