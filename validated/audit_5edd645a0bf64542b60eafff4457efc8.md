This confirms the vulnerability. `Utils::HmacValidator.validate` computes the HMAC only over `to_signable_string`, which for `Webhooks::Request` is `@raw_body` alone [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values are pulled straight from HTTP headers with no cryptographic binding to that HMAC [2](#0-1) . `Registry.process` validates only the HMAC, then hands `request.shop` straight to the handler as the tenant identifier [3](#0-2) , and the documented handler contract explicitly instructs apps to key off `data.shop` for tenant routing [4](#0-3) .

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC, allowing cross-tenant impersonation via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated headers. `Registry.process` trusts `Utils::HmacValidator.validate(request)` (body-only check) as proof of authenticity for the whole request, then forwards the unauthenticated `shop` header value to the app's webhook handler as the tenant identifier.

### Finding Description
The equality this code should enforce is: `shop header used for tenant attribution == shop that the HMAC actually authenticates`. It does not hold, because:

- `Utils::HmacValidator#validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received `hmac` [5](#0-4) .
- For webhooks, `to_signable_string` returns only `@raw_body` [1](#0-0) .
- `shop`, `topic`, `webhook_id`, and `api_version` are all derived from separate HTTP headers that are never included in the signable string [2](#0-1) .
- `Registry.process` gates only on `Utils::HmacValidator.validate(request)` and then constructs `WebhookMetadata` using `request.shop` (header) alongside `request.parsed_body` (HMAC-covered) as if both were equally trustworthy [6](#0-5) .

Because the HMAC secret is per-app (not per-shop), any tenant that has installed the app can legitimately receive a webhook with a valid `hmac-sha256` for some body. Since the header carrying the shop identity is not part of the signed material, that same (body, hmac) pair remains valid if replayed with a different `shopify-shop-domain` header. The library provides no defense against this at the point where it hands data to the app: it treats `request.shop` as authenticated when it is not bound to the signature.

### Impact Explanation
This breaks the tenant isolation boundary the gem is documented to provide. The webhook doc instructs integrators to key tenant-specific logic directly off `data.shop` [4](#0-3) , so a header value that is not authenticated by this library is used, by design, as a tenant identifier. An attacker who installs the app on their own shop (or otherwise obtains one valid `(raw_body, hmac)` pair) can replay it against the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop, causing the handler to process attacker-controlled body content under a victim tenant's identity — a cross-tenant data-integrity/impersonation issue.

### Likelihood Explanation
Moderate-to-high: it requires only (1) the ability to send arbitrary HTTP requests to the app's public webhook endpoint, and (2) possession of one valid `(body, hmac)` pair, which any attacker can obtain simply by installing the target app on a shop they control (a standard, unprivileged action) and capturing the webhook Shopify sends them. No `api_secret_key`, access token, or other privileged credential is needed.

### Recommendation
Bind the shop (and ideally topic/webhook-id) identity to the authenticated material before trusting it:
- Include `shop-domain` (and `topic`) in the signable string used for HMAC verification, if compatible with Shopify's signing scheme, or
- Cross-validate the header-derived `shop` against an independently authenticated source (e.g., the shop associated with the stored session/webhook subscription that the `webhook_id` maps to) before dispatching to the handler, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be used alone for tenant attribution, and provide a verified alternative.

### Proof of Concept
1. Attacker creates a Shopify development/trial store and installs the target app, registering for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of raw body>`, and some JSON body.
3. Attacker captures the exact `raw_body` and `X-Shopify-Hmac-Sha256` value.
4. Attacker sends a new HTTP request directly to the app's public webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the raw body against the HMAC. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` line 198 builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches attacker-controlled body content to the app's handler as if it originated from the victim shop.

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

**File:** docs/usage/webhooks.md (L12-26)
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
