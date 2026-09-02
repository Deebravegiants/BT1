I have enough evidence to finalize the analysis.

### Title
Webhook `shop-domain` Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` authenticates the payload bytes but never the `x-shopify-shop-domain` (or `shopify-shop-domain`) header. `ShopifyAPI::Webhooks::Registry.process` still trusts `request.shop` verbatim when building `WebhookMetadata` passed to the app's handler, so the shop identity delivered to app logic is unauthenticated even though the request "passed HMAC validation."

### Finding Description
`Request#to_signable_string` is defined as just `@raw_body` [1](#0-0) , and `HmacValidator.validate`/`validate_signature` compute and compare the HMAC solely over that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all read directly from HTTP headers with no cryptographic binding to the signature [3](#0-2) .

`Registry.process` gates only on `Utils::HmacValidator.validate(request)` and then forwards `request.shop` unchanged into `WebhookMetadata`, which is delivered to the app's registered handler as the shop identity for that event [4](#0-3) . The documented handler contract explicitly tells app authors that `data.shop` is "The shop domain of the webhook" and is safe to key business logic on (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [5](#0-4) .

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not per-tenant), any merchant who installs the app receives genuine webhook deliveries with a valid `(body, hmac)` pair signed with that same secret [6](#0-5) . Since the header carrying the shop identity is outside the signed material, that attacker-observed `(body, hmac)` pair remains valid when replayed to the app's public webhook endpoint with an arbitrary forged `x-shopify-shop-domain` header. `Registry.process` will accept it (HMAC checks out) and hand the handler a `WebhookMetadata` claiming the event came from a victim shop, when in fact the body/topic belong to the attacker's own store. This breaks the identity binding: `shop authenticated by HMAC` should equal `shop delivered to handler`, but here the HMAC never covers the shop field at all.

### Impact Explanation
This is a cross-tenant confused-deputy vector: an attacker who merely installs the app on their own shop can cause the host application to process fabricated events attributed to any other shop domain of their choosing, while the request still passes this gem's own signature check. Depending on how the host app's handler uses `data.shop` (e.g., mandatory topics like `app/uninstalled`, `customers/redact`, `shop/redact` are exactly the kind of security-relevant lifecycle events this gem special-cases [7](#0-6) ), this can lead to session/token invalidation, data deletion, or state corruption falsely attributed to a shop the attacker doesn't control — a cross-tenant impact.

### Likelihood Explanation
Any developer or attacker can install the target app on a shop they control (a normal, unprivileged action), capture the legitimate webhook `(raw_body, hmac)` pair Shopify sends them, and replay it to the app's public webhook callback URL with a modified shop-domain header. No secrets, tokens, or privileged access are required beyond running an app install, which any internet user with a Partner/development store can do.

### Recommendation
Bind the shop identity to the authenticated material: include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header value in `to_signable_string`, or independently verify that `request.shop` corresponds to a shop with an active, previously-established session/webhook registration for the topic before invoking the handler, rather than trusting the header as-is once HMAC-over-body-only passes.

### Proof of Concept
1. Install the target Shopify app on `attacker-shop.myshopify.com`.
2. Capture a legitimate incoming webhook request at the app's callback endpoint, noting the raw body and the `x-shopify-hmac-sha256` header value (both are valid and will pass `HmacValidator.validate` because they are genuinely HMAC'd with the app's `api_secret_key`).
3. Replay the identical `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` computes the HMAC over `raw_body` only [1](#0-0) , finds it valid, and invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` [8](#0-7) , even though the event actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
