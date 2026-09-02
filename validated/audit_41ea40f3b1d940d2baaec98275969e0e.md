Confirmed root cause. The finding is solid and ready to report.

### Title
Webhook `shop` (tenant) identity is taken from an unauthenticated header, not bound to the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`, `webhook_id`, `api_version`) from HTTP headers, while `ShopifyAPI::Utils::HmacValidator` only authenticates the raw request body. The library never binds the header-derived shop domain to the cryptographic signature, so an attacker who has ever received one genuine webhook (with a valid body+HMAC pair) for their own store can replay that exact body to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop, and the request will still pass HMAC validation.

### Finding Description
`Registry.process` treats a webhook as authentic solely based on the body HMAC check: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `to_signable_string`, which for webhooks is defined to be only the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are never mixed into the signed string: [3](#0-2) 

`HmacValidator.validate_signature` compares only the computed body signature to the received one — headers play no role in the comparison: [4](#0-3) 

The unauthenticated `shop` value is then handed directly to the app's handler as the tenant identity, exactly as documented for consuming apps to use: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `shop_authenticated_by_hmac == shop_used_by_handler`. In this implementation that equality is never enforced — the HMAC only proves "some request body was produced by a holder of `api_secret_key`," while `shop` (and `topic`/`webhook_id`) are attacker-controlled header values that ride along unverified.

Since `api_secret_key` (the app's client secret) is shared across every shop that installs the app, any shop — an "unprivileged" merchant relative to other tenants of the same app — can act as a valid source of genuinely-signed body/HMAC pairs. That merchant can capture one webhook delivery for their own store, then re-POST the identical raw body and HMAC to the app's public webhook endpoint with the `shopify-shop-domain` header rewritten to any victim shop. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` forwards `WebhookMetadata` claiming the victim's shop with attacker-supplied body content to the app's handler.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee to consuming apps: the documented contract is that `data.shop` in a `WebhookMetadata` passed to a handler can be trusted as the shop that Shopify authenticated the webhook for. Because the shop identity is unauthenticated, a shop with the app installed can inject arbitrary "shop X did Y" events for any other shop X into the app's business logic (e.g. triggering `orders/create`-driven side effects, `app/uninstalled` cleanup, or GDPR `customers/redact` handling) attributed to a victim tenant — a cross-tenant access/data-integrity issue rated Critical per the given impact list.

### Likelihood Explanation
Exploitation requires no privileged credentials, no `api_secret_key`, and no access token — only that the attacker has (or creates) their own installation of the target app, a capability trivially available to any Shopify merchant/developer, and the ability to send arbitrary HTTP requests to the app's public webhook callback URL (which must be internet reachable to receive real Shopify webhooks). This fits the "unprivileged internet user" threat model.

### Recommendation
Bind the header-derived identity fields into the value that is HMAC-verified, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the signature (e.g., include them in `to_signable_string`, or require the consuming app to independently corroborate the shop against a known/installed-shop list before trusting webhook headers). At minimum, document prominently that `data.shop`/`data.topic` are NOT covered by the HMAC and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. App A is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (same `client_id`/`client_secret`, i.e. the same `ShopifyAPI::Context.api_secret_key`).
2. Shopify sends a genuine webhook to the app for `attacker-shop.myshopify.com`, e.g.:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC over body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "hello"}
   ```
   The attacker captures this exact body and HMAC (they control the shop, so they can trivially inspect delivered webhooks, or simply craft any body — the HMAC will be valid for it because they can trigger app-side actions to produce whatever body content they like on their own store).
3. Attacker replays the identical body+HMAC to the same endpoint, changing only the header:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC — body unchanged>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id": 1, "note": "hello"}
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and matches — validation passes.
5. `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: {...}, ...)` is passed to the app's handler, which processes attacker-supplied data as if it legitimately originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
