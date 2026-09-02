### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` value that is subsequently handed to the host application's handler as the tenant identifier is taken from an unauthenticated HTTP header and is never part of the signed content. This mirrors the reported bug class: a value that is *acted upon* (here, the tenant/shop binding) is not actually *covered* by the integrity check (here, the HMAC) that is supposed to authenticate the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, independent of the signature: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.shop` as the tenant identifier when building `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirms the signature is computed only from `verifiable_query.to_signable_string`, i.e. the body, using the app's single, shop-independent `api_secret_key`: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by the HMAC == shop delivered to the handler as the tenant key`. Because `shop` is excluded from the signed content, and the app's `api_secret_key` is the same across every shop that installs the app, any party who can obtain one validly-signed `(body, hmac)` pair for the app (e.g., from a webhook delivered to their own dev/test store — a routine, unprivileged interaction) can resubmit that exact body+hmac pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still succeed (it never inspects the shop header), and `Registry.process` will hand the attacker-chosen body to the handler labeled with an attacker-chosen `shop`, per the documented handler contract: [5](#0-4) [6](#0-5) 

### Impact Explanation
Every host application built on this gem's documented pattern uses `data.shop` from `WebhookMetadata` as the tenant key to route/store/process the webhook payload (per the gem's own example: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`). Since the shop label is unauthenticated, an unprivileged actor can cause the host app to ingest and persist attacker-controlled data under a victim tenant's identity — a cross-tenant data-integrity break. This fits the Critical "cross-tenant access" category since the gem's own signing/verification contract silently omits the very field (`shop`) that host applications are told to trust for multi-tenant dispatch.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install/receive at least one genuine webhook for the target app on an account the attacker controls (trivial for any public app, or achievable by simply observing one real webhook delivery), and (2) the ability to POST to the app's public webhook endpoint (by design, an unauthenticated public endpoint, since `Registry.process` is the sole authentication gate). No access token, `client_secret`, or TLS interception is needed — the entire exploit is possible with unprivileged internet access to the webhook endpoint and one legitimately observed webhook payload.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the HMAC-signed content, or otherwise cryptographically bind `shop` to the payload before exposing it via `WebhookMetadata`. At minimum, document/enforce that host applications must independently verify that `shop` corresponds to a shop with an active, registered subscription for that specific `webhook_id`/topic before trusting it, and consider deduplicating/binding webhook_id to the specific shop it was registered for.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g., `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac over raw body B>`, and raw body `B`.
3. Attacker (or a script under the attacker's control, since this is their own delivered request or one they can freely trigger/observe) captures `B` and the valid `hmac`.
4. Attacker sends a new POST directly to the app's public webhook endpoint with the same raw body `B` and same `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` succeeds because it only checks `B` against the secret; `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)`, exactly as shown in `Registry.process`: [3](#0-2) 
6. The host application, following the gem's documented pattern, processes/stores attacker-controlled body `B` as if it belonged to `victim.myshopify.com`.

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
