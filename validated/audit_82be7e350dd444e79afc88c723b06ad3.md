Confirmed. The `AuthQuery#to_signable_string` includes `shop` in the HMAC-signed payload for OAuth [1](#0-0) , but `Webhooks::Request#to_signable_string` only signs `@raw_body`, never the `shop-domain` header [2](#0-1) . `HmacValidator.validate` only checks `to_signable_string` against the HMAC, so `request.shop` is trusted without being part of the signed bytes [3](#0-2) . `Registry.process` passes this unverified `shop` straight into `WebhookMetadata` given to the app's handler as the tenant identifier [4](#0-3) [5](#0-4) , and the documented handler pattern uses `data.shop` to key work per shop [6](#0-5) .

### Title
Webhook `shop` domain is not covered by HMAC signature, allowing cross-tenant spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw body when validating the webhook HMAC, while the `shop` (and `topic`/`api_version`/`webhook_id`) values come from headers that are entirely excluded from the signed payload. Any party who can produce a body/HMAC pair valid for the app's secret (e.g., the legitimate holder of a webhook subscription for their own shop) can attach an arbitrary `x-shopify-shop-domain` header, and the gem will pass that unverified shop value on to the app's webhook handler as if it were verified.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it with `verifiable_query.hmac` [7](#0-6) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [8](#0-7) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers with no binding to the signature [9](#0-8) . `Registry.process` only calls `Utils::HmacValidator.validate(request)`, which validates the body, then constructs `WebhookMetadata` using `request.shop` unchanged [4](#0-3) . This breaks the equality that should hold: `shop authenticated by HMAC == shop delivered to the handler`. Contrast this with the OAuth flow, where `AuthQuery#to_signable_string` explicitly folds `shop` into the signed query string [1](#0-0) , showing the gem's own established pattern for binding a tenant identifier to its HMAC — a pattern not followed by `Webhooks::Request`.

### Impact Explanation
Because the `shop` field is unauthenticated, an attacker who controls (or compromises) delivery of one legitimately-HMAC-signable webhook payload — e.g., a merchant/attacker who has installed the app on their own shop and thus can send a body whose HMAC validates against the app's shared secret — can set the `shop-domain` header to any victim shop's domain. The host application's handler, following the gem's documented contract (`data.shop`) [10](#0-9) , will process that payload as if it originated from the victim tenant. Depending on how the host app uses `data.shop` (e.g., to look up per-shop state, enqueue per-shop jobs, or update per-shop records), this enables cross-tenant data injection/corruption without needing the victim's access token.

### Likelihood Explanation
Exploitation only requires the ability to produce one payload whose HMAC is valid for the app's `client_secret`-derived key — achievable by any shop that has installed the app and can trigger a real webhook (or replay one they legitimately received), then re-deliver it to the app's webhook endpoint with a forged `shop-domain` header, since nothing in the gem checks that the header matches an actual registered/expected shop for that HMAC. No access token or leaked secret is required.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the bytes that are HMAC-verified for webhook requests, or otherwise cryptographically bind the `shop-domain` header to the signed payload before trusting it in `WebhookMetadata`. At minimum, cross-check `request.shop` against an app-maintained registry of shops that are expected to receive this webhook_id/topic before dispatching to the handler.

### Proof of Concept
1. App shop `attacker.myshopify.com` installs the app and legitimately receives (or triggers) a webhook, giving the attacker a valid `raw_body` + `x-shopify-hmac-sha256` pair signed with the app's secret.
2. Attacker replays this exact `raw_body`/HMAC pair to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `raw_body` is checked [11](#0-10) .
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [12](#0-11)  and performs shop-scoped work against `victim.myshopify.com` on the attacker's behalf.

### Citations

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L34-43)
```ruby
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** docs/usage/webhooks.md (L12-27)
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
```
