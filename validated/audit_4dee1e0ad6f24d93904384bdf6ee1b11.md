Confirmed: `WebhookMetadata` at [1](#0-0)  carries `topic`, `shop`, `api_version`, and `webhook_id` — all sourced straight from HTTP headers via `Request#topic`/`#shop`/`#api_version`/`#webhook_id` [2](#0-1) , while `to_signable_string` (what `HmacValidator` actually verifies) is only the raw body [3](#0-2) . `Registry.process` gates only on that body HMAC and then forwards the unauthenticated `shop`/`topic` straight to the app handler [4](#0-3) .

### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` binds only the raw HTTP body into the HMAC-signable string, while the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's `WebhookHandler` come from unauthenticated headers.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the app's shared `Context.api_secret_key` [5](#0-4) . For a webhook `Request`, `to_signable_string` returns only `@raw_body` [3](#0-2) ; `hmac` is computed only from the `hmac-sha256` header [6](#0-5) . Crucially, this is the app-wide `api_secret_key` — the same secret is used to validate webhooks for every shop that has this app installed, it is not shop-specific.

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching [4](#0-3) , then builds `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all of which are read straight off headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) with no cryptographic binding to the signed body [2](#0-1) .

The broken identity equality is: `hmac_verifies(raw_body)` is treated as if it implies `shop_header == originating_shop`, but the HMAC never covers `shop` (or `topic`). Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's secret — e.g., by triggering a webhook event on their own, unprivileged, self-owned installation of the app — can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header (any `*.myshopify.com` string) and an arbitrary `shopify-topic` header. `HmacValidator.validate` still returns `true` because it only re-derives the signature over `@raw_body`, and `Registry.process` forwards the attacker-chosen `shop` and `topic` to the app's handler as if authenticated.

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately controls only their own shop/installation can forge webhook events that the app's handler will process as though they originated from a different, victim shop, and/or under a different topic than the one actually signed (including sensitive topics like uninstall or compliance topics unless separately mandated to bypass the registry, see `MANDATORY_TOPICS` handling) [7](#0-6) . Since `WebhookHandler#handle` implementations are documented to key persistence/business logic off `data.shop` and `data.topic` [8](#0-7) , this enables cross-tenant data corruption/impersonation without needing the app's `client_secret` or any privileged account for the victim shop — only an ordinary account owning any store where the app is installed.

### Likelihood Explanation
Any unprivileged user can install a public app on their own development/trial store, trigger an event they control (e.g., `orders/create` with attacker-chosen body content) to obtain a genuinely-signed `(raw_body, hmac)` pair, then send a crafted HTTP request straight to the app's webhook endpoint with the same body/HMAC but forged `shop-domain`/`topic` headers. No secrets, tokens, or victim cooperation are required.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signable string (or otherwise cryptographically bind them, e.g. by validating `shop` against an actual stored session/shop record before trusting it), so header values cannot be swapped independently of the signed body.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., creates an order), capturing the genuine request: body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`, per `lib/shopify_api/webhooks/request.rb` line 12 and `hmac_validator.rb` lines 27-31).
2. Attacker sends a new HTTP request to the app's webhook receiver with the same body `B` and same `x-shopify-hmac-sha256: H`, but headers:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: orders/create` (or any registered topic)
3. `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` and it matches `H`, so validation passes (`lib/shopify_api/webhooks/registry.rb` line 190).
4. `Registry.process` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: JSON.parse(B), ...)` and invokes the registered handler, which processes the attacker-supplied body as if it belongs to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L249-254)
```ruby
        # Mandatory webhooks are subscribed to via the partner dashboard not the API
        # https://shopify.dev/docs/apps/webhooks/configuration/mandatory-webhooks
        sig { params(topic: String).returns(T::Boolean) }
        def mandatory_webhook_topic?(topic)
          MANDATORY_TOPICS.include?(topic)
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
