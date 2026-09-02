### Title
Webhook shop/topic/api-version/webhook-id headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signable content from the raw request body only, while the shop domain, topic, api version and webhook id are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` (taken from the header) to build the `WebhookMetadata` handed to the app's handler, breaking the binding between "the shop whose data was HMAC-signed" and "the shop the app processes the webhook as."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled from HTTP headers that are never part of the signed content: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` field: [4](#0-3) 

`Registry.process` checks this HMAC, then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` — none of which were part of what was verified — and forwards it as trusted data to the app's registered handler: [5](#0-4) 

The identity binding that should hold is: `shop_that_the_HMAC_proves_owns_this_body == shop_the_app_processes_this_webhook_as`. Because the header is outside the signed bytes, an unprivileged internet user who owns any Shopify store can capture a legitimately Shopify-signed webhook body for their own shop (e.g. `orders/create`) and replay it to the target app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or topic/api-version/webhook-id) header rewritten to a victim shop. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` passes the forged shop identity straight into the handler as if Shopify itself asserted it.

### Impact Explanation
Any app built on this library that keys per-tenant behavior off `WebhookMetadata#shop` (e.g., looking up the stored access token/session for that shop, updating that shop's local records, or triggering actions scoped to that shop) will act on attacker-controlled body content while believing it originates from an arbitrary victim shop of the attacker's choosing. This is a cross-tenant identity confusion rooted entirely in this gem's verification logic, not enforced host-application misuse: the gem asserts the webhook is HMAC-valid ("Invalid webhook HMAC." is the only check raised) while silently handing over an unauthenticated shop identity for the app to trust.

### Likelihood Explanation
The attacker only needs their own installed app/shop that can receive webhooks (no `api_secret_key`, no victim's access token, and no privileged access to the target). Capturing one legitimately-signed webhook payload for their own shop and replaying it with a rewritten `Shop-Domain`/topic header against the victim app's public webhook endpoint is trivial and repeatable for any topic the app subscribes to.

### Recommendation
Include the shop domain (and topic/api-version/webhook-id if they drive branching) in the HMAC-signed content, or otherwise cryptographically bind them to the verified body (e.g., require the app to independently confirm the shop is one it has an active session/install for before trusting `WebhookMetadata#shop`, and document that header fields are unauthenticated). At minimum, `Request#to_signable_string` should not be the sole basis for asserting the trustworthiness of `Request#shop`.

### Proof of Concept
1. Attacker installs the target app-type integration on their own store `attacker.myshopify.com` and lets Shopify send a legitimate webhook, e.g. `orders/create`, to any endpoint the attacker controls, capturing the raw body and its valid `X-Shopify-Hmac-Sha256` header.
2. Attacker computes nothing further — the HMAC only ever covered the body — and replays the exact same body + hmac header to the victim app's public webhook URL, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (topic/api-version/webhook-id can likewise be forged).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes since it only checks the raw body against the real secret used to sign the attacker's own legitimate webhook (the shared `api_secret_key` is the same for every shop calling this app, so any of the app's own valid webhooks pass this check regardless of which shop header is attached):
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
4. The handler receives `WebhookMetadata#shop == "victim-shop.myshopify.com"` alongside attacker-controlled body content, and the app processes/attributes attacker data to the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
