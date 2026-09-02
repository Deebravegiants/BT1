This confirms the root cause. The `shop-domain` header is used by `ShopifyAPI::Webhooks::Request#shop` (and passed directly to the app's handler as the tenant identifier `data.shop`), but `Request#to_signable_string` returns only `@raw_body`, so the HMAC signature validated by `Utils::HmacValidator.validate` never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers.### Title
Webhook shop-domain identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight to the app's handler as the trusted tenant identifier. Because the `shop-domain` header (along with `topic`, `webhook-id`, `api-version`) is never part of the signed bytes, any holder of one valid `(body, hmac)` pair — which is trivially available to any merchant who installs the app on their own store and receives a real webhook — can replay that exact body/hmac while substituting an arbitrary `shop-domain` header, causing the app to process/attribute that webhook payload to a different tenant.

### Finding Description
The webhook processing entry point is `Registry.process`: [1](#0-0) 

It validates authenticity using `Utils::HmacValidator.validate(request)`: [2](#0-1) 

The signable content comes from `VerifiableQuery#to_signable_string`, which for `Webhooks::Request` is defined as just the raw body: [3](#0-2) 

But the `shop` value that the gem hands to the app's handler is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the body or hmac: [4](#0-3) 

That header value flows unchanged into `WebhookMetadata#shop`, which the gem's own documentation instructs app developers to trust as the tenant/shop identifier for routing and persistence: [5](#0-4) [6](#0-5) [7](#0-6) 

The broken identity binding is:
`shop_used_by_handler (WebhookMetadata#shop, from request.shop header)` ≠ `shop_bound_by_hmac (none — to_signable_string covers only @raw_body)`

Since a single app-level `api_secret_key` (the app's client secret) is shared across every shop that installs the app — not scoped per-shop — any merchant who has installed the app legitimately receives a validly-HMAC-signed webhook for their own shop. They can capture that `(raw_body, hmac)` pair and re-POST it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` will still succeed (it never looked at the header), and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain while the body content is the attacker's real (and attacker-controlled, insofar as they can trigger events like `orders/create`, `customers/data_request`, etc. on their own store) payload.

### Impact Explanation
This directly enables cross-tenant data confusion/exfiltration: an app that persists webhook data keyed by `data.shop` (exactly as shown in the gem's own usage example, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to associate one merchant's data/events with another merchant's tenant record, or to trigger tenant-specific side effects (e.g., mandatory GDPR webhooks like `customers/redact`, `shop/redact`) against an unrelated shop. This matches the Critical "cross-tenant access" impact category, since the vulnerability lets one authenticated app-installer corrupt or read another tenant's webhook-driven state without possessing that tenant's credentials.

### Likelihood Explanation
Likelihood is high for any developer following the gem's documented pattern of trusting `data.shop`, since the attack requires nothing beyond: (1) installing the app on an attacker-controlled store (a normal, low-privilege action any merchant can perform), (2) capturing a legitimate webhook's raw body + `x-shopify-hmac-sha256` value, and (3) replaying it with a forged `x-shopify-shop-domain` header to the app's known webhook endpoint. No access token, `client_secret`, or privileged credential of the victim tenant is required.

### Recommendation
Bind the shop identity to the signed payload before trusting it: either include `shop-domain` (and `topic`/`webhook-id`) inside the HMAC-signed bytes (`to_signable_string`) in `lib/shopify_api/webhooks/request.rb`, or have `Registry.process`/`HmacValidator` cross-check the header-derived shop against an independently verified source (e.g., look up the expected shop for the associated `webhook_id`/subscription, or require the consuming app to validate `shop` against its own known/installed shop list before trusting `WebhookMetadata#shop`). At minimum, the gem's documentation should explicitly warn that `data.shop` is not part of the authenticated payload and must be independently verified by the host application against its installed-shop records before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify sends the app a legitimate webhook:
   ```
   POST /webhooks/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {"id":1,"note":"attacker-controlled content"}
   ```
3. Attacker captures this exact `(body, hmac)` pair (they control the traffic to their own endpoint, or can trigger/observe it via test tooling) and replays it directly to the app's public webhook endpoint with the header changed:
   ```
   POST /webhooks/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac-of-same-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {"id":1,"note":"attacker-controlled content"}
   ```
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `@raw_body` only, matches successfully, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {...attacker content...})`, causing the host app to attribute attacker-controlled data to the victim tenant.

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

**File:** docs/usage/webhooks.md (L12-29)
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
