### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via the HMAC over the raw request body, while the shop identity (`shop-domain` header, surfaced as `Request#shop`) and other metadata (`topic`, `webhook-id`, `api-version`) are read from unauthenticated HTTP headers and never included in the signed payload. Because the same app-level `client_secret` signs webhooks for every shop that installs the app, any merchant (an unprivileged internet user relative to other tenants) who receives a legitimately-signed webhook for their own store can replay that valid `(body, hmac)` pair against the app's webhook endpoint while substituting an arbitrary `shop-domain` header, causing the host app to process attacker-supplied webhook data attributed to a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery#to_signable_string` by returning only the raw body: [1](#0-0) 

All other fields exposed by `Request` — `shop`, `topic`, `api_version`, `webhook_id` — are pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only this body-only HMAC before dispatching to the app's handler with the header-derived `shop`: [3](#0-2) 

The equality this breaks: the app implicitly expects `shop_that_signed_the_payload == shop_delivered_in_WebhookMetadata`, but the gem only proves `hmac_valid(body)`; it never proves `hmac_valid(body, shop)`. Since `Context.api_secret_key` (and `old_api_secret_key`) is a single per-app secret shared across every shop that installs the app (see `HmacValidator.validate`, which signs/verifies with `Context.api_secret_key`): [4](#0-3) 

a malicious merchant who has installed the app can legitimately trigger a real webhook for their own shop (e.g. by placing an order, or via `Registry.register` /any topic they control), capture the valid `(raw_body, x-shopify-hmac-sha256)` pair, then POST it to the app's webhook endpoint with a forged `x-shopify-shop-domain` header set to a victim shop's domain (and optionally a forged `topic`/`webhook-id`). `Registry.process` will validate the HMAC successfully (it only checks the body) and hand the app's registered handler a `WebhookMetadata` claiming the data came from the victim shop.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: an app handler that keys off `WebhookMetadata#shop` (the documented/intended usage per `docs/usage/webhooks.md`, e.g. to load the shop's session, or to react to `app/uninstalled`, `shop/redact`, order events, etc.) can be made to act on/for a shop the attacker does not control, using data the attacker fully controls. This is a cross-tenant access vector as defined in scope (Critical impact category), since the identity of "which shop is this webhook for" is not authenticated, only the payload bytes are.

### Likelihood Explanation
Requires only that the attacker be a legitimate (even free/trial) merchant installer of the target app — no leaked secrets, no privileged account, no TLS interception. This satisfies the "unprivileged internet user" bar. The only friction is guessing/knowing a target shop's `.myshopify.com` domain, which is generally discoverable/public.

### Recommendation
Bind the shop (and ideally topic) identity into the verified signature space, or otherwise revalidate the header-derived shop against an authenticated source before dispatch:
- Prefer verifying the delivered webhook against Shopify by confirming the shop is one your app has an active session/install record for, and cross-check that the `shop-domain` header matches the shop associated with the specific `webhook_id` fetched via an authenticated Admin API call, rather than trusting the header outright.
- At minimum, document prominently in `Registry.process`/`Request` that `shop`, `topic`, `webhook_id`, and `api_version` are unauthenticated header values and must not be trusted for tenant-isolation decisions without additional verification by the host app.

### Proof of Concept
1. Attacker signs up as a normal merchant and installs the vulnerable app, receiving legitimate webhooks (app secret is shared across all installs).
2. Attacker triggers/captures a real webhook delivery: `raw_body`, `x-shopify-hmac-sha256`, `x-shopify-topic`.
3. Attacker replays the same `raw_body` + `hmac` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (== `raw_body`) — validation succeeds.
5. The app's handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)` and performs actions/logic scoped to the victim shop using attacker-controlled data.

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
