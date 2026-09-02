### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then passes the caller-supplied `shop-domain` header straight through to the app's handler as the tenant identity, with no cryptographic binding between the two.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` simply reads the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header verbatim [2](#0-1) . `Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which computes the HMAC exclusively over `to_signable_string` (i.e., the raw body) [3](#0-2) , and then immediately forwards `request.shop` (the raw header) to the app-registered handler as the trusted tenant identifier, without re-deriving or verifying it against anything signed: [4](#0-3) .

This breaks the identity binding: `HMAC(raw_body, api_secret_key) == valid` should imply `shop-domain == the shop that generated this body`, but the shop header is never part of the signed bytes, so that equality does not hold. Anyone who has captured or replayed one legitimately-HMAC-signed webhook body from *any* shop that uses the same app (e.g., their own development/test store, or a payload obtained via another disclosure channel) can resubmit that exact body with an arbitrary `shop-domain` / `x-shopify-shop-domain` header value naming a victim shop, and the library will report it as an authenticated, HMAC-valid webhook for the victim tenant. Handlers that trust `data.shop` (as the library's own documentation instructs them to [5](#0-4) ) to key database writes, cache invalidation, deduplication, session/store lookups, or job dispatch (`perform_later(topic: data.topic, shop_domain: data.shop, ...)` per the gem's own usage example [6](#0-5) ) can be tricked into attributing the body's data to the wrong tenant — a cross-tenant data-confusion/write primitive.

### Impact Explanation
This is a Critical-class issue under "cross-tenant access": the gem's `Registry.process` API is the only authentication boundary between an inbound HTTP request and the trusted `WebhookMetadata` object handed to application code, and the `shop` field of that trusted object is derived from unauthenticated bytes (the header) despite the HMAC check passing. Any app that follows the documented pattern of trusting `data.shop` for tenant scoping (exactly as the gem's own docs recommend) is exposed to cross-tenant data corruption/impersonation without needing the app's `client_secret` or an access token — only a single validly-signed webhook body (which every merchant/dev store using the app legitimately receives).

### Likelihood Explanation
Reachable by any unprivileged internet user who can obtain one legitimately HMAC-signed webhook payload for the shared app (trivially available to any developer or merchant who installs the app, since HMAC secrets are per-app, not per-shop) and can then POST that same raw body with a forged shop header to the app's public webhook endpoint, using the exact API contract (`Registry.process(Request.new(raw_body:, headers:))`) the gem itself documents.

### Recommendation
Include `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signed body, so that `to_signable_string`/`HmacValidator.validate` cannot pass for a body whose declared shop was altered.

### Proof of Concept
1. Install the target app on Shop A (attacker-controlled) and Shop B (victim), both using the same `client_secret`.
2. Capture a legitimate webhook delivery to Shop A: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for `B`).
3. Replay a POST to the app's webhook endpoint with the same raw body `B` and the same valid HMAC `H`, but set `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds [7](#0-6) ; it then dispatches to the handler with `shop: "shop-b.myshopify.com"` even though the body actually originated from Shop A [4](#0-3) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L19-29)
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
