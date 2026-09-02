### Title
Webhook shop-domain (and topic/api-version/webhook-id) headers are trusted without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that raw body. The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers and are never included in the signed data. `Registry.process` passes the unauthenticated `shop` header value directly to the app's `WebhookHandler` as the tenant identifier, breaking the intended binding: `HMAC-verified-bytes == bytes-the-app-acts-on`.

### Finding Description
`Request#to_signable_string` is defined as just the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors pull unauthenticated header values that are not part of that signable string: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` only ever computes/compares the HMAC over `verifiable_query.to_signable_string` (the body), never over the headers: [3](#0-2) 

`Registry.process` checks only that HMAC, then forwards `request.shop` (the header value) unchanged into `WebhookMetadata`, which the host app's handler is documented to use as the shop/tenant identifier for the webhook: [4](#0-3) [5](#0-4) 

The gem's own documentation confirms `data.shop` is meant to identify "the shop domain of the webhook" and is expected to be used by the app (e.g., to enqueue per-shop work): [6](#0-5) 

This is the same bug class as the report: a field that is acted upon (`shop`, used as the tenant key) is not covered by the cryptographic check (`hmac`, computed over body only) — equivalent to `verified_bytes != bytes_acted_on`. Concretely: `to_signable_string() == raw_body`, but `Registry.process` acts on `request.shop`, so the invariant `signed_data ⊇ acted_on_data` is violated.

### Impact Explanation
Any actor who can obtain one genuine `(raw_body, hmac)` pair signed by Shopify with the app's `client_secret` — trivially achievable by an attacker who installs the target app on their own store and triggers a webhook (e.g., creates an order) — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will deliver a `WebhookMetadata` with the attacker-chosen `shop` value and the attacker's own body/topic to the handler. If the host application uses `data.shop` to look up a session/access token or to write per-tenant data (as the docs recommend), this allows cross-tenant confusion: an attacker can cause the app to process or record fabricated webhook data under a victim shop's identity, or trigger the app's business logic (e.g., data-request/redact handling, order-created side effects) attributed to a shop that never sent it.

### Likelihood Explanation
Likelihood is moderate: the attacker needs their own capacity to legitimately install the app (many apps are freely installable) and to know/guess a target shop's domain (public information: `*.myshopify.com`), both of which are low-effort for an "unprivileged internet user." No access token, `client_secret`, or privileged account is required — only observation of a legitimate webhook the attacker can generate for their own tenant.

### Recommendation
Include the tenant-identifying and routing fields (`shop`, `topic`, `api_version`, `webhook_id`) in the HMAC-covered signable data, or otherwise cryptographically bind the header values to the verified payload (e.g., by validating them against Shopify's webhook delivery metadata via a signed envelope, or requiring TLS-authenticated, allow-listed source IPs in addition to HMAC). At minimum, document/enforce that `request.shop` must never be trusted as an authorization or tenant boundary unless it is independently confirmed to match the shop associated with the registered webhook subscription.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a subscribed webho

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
