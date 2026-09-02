### Title
Webhook `shop-domain`/`topic`/`webhook-id` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while the shop identity (`shop-domain` header, exposed as `request.shop`) and other metadata (`topic`, `webhook-id`) are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC only against this body-only signable string, so the tenant-identifying header is never bound to the signature that is checked before the webhook is dispatched to the host application's handler.

### Finding Description
`Webhooks::Registry.process` gates webhook handling on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

The validator computes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` header value using `OpenSSL.secure_compare`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, and `shop`, `topic`, and `webhook_id` are all pulled straight from HTTP headers that are never mixed into the signed string: [3](#0-2) 

This breaks the intended identity binding: **the shop attribution used by the host application (`request.shop`) is not equal to the shop that the HMAC actually authenticates (only the body bytes)**. Shopify's webhook HMAC secret (`Context.api_secret_key`) is per-app, not per-shop — every shop that has the app installed produces webhooks signed with the *same* secret. Consequently, a valid `(raw_body, hmac)` pair captured from any shop that has the app installed (including a shop an attacker controls, e.g., a free/dev store) remains a cryptographically valid signature no matter what `shop-domain`, `topic`, or `webhook-id` header values are attached to the replayed request, because those fields are not part of what was signed.

`Registry.process` then constructs `WebhookMetadata` directly from these unauthenticated header values and hands it to the app's webhook handler: [4](#0-3) 

Any consuming application that trusts `data.shop` from a successfully-`process`ed webhook (which is the documented, intended use of this API) will act on attacker-chosen tenant identity while still seeing `HmacValidator.validate` report success.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who can obtain any one validly-signed webhook body for the app (trivial if the attacker installs the app on their own store, since real Shopify webhook deliveries are signed with the shared app secret and delivered to the app's public webhook endpoint) can replay that body with a forged `shop-domain` header naming a victim shop. `HmacValidator.validate` still returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:12-31`), and `Registry.process` forwards a `WebhookMetadata` claiming to be from the victim shop (`lib/shopify_api/webhooks/registry.rb:198-199`). Any host application logic keyed off `data.shop` (e.g., looking up the victim's stored session/access token, updating victim-shop records, or triggering victim-shop side effects) is fed attacker-controlled, mis-attributed data — a cross-tenant access/data-injection vector satisfying the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Requires no privileged credentials: the attacker needs only (a) network access to the app's public webhook endpoint and (b) one legitimately-signed webhook body, obtainable for free by installing the app on any store (including the attacker's own) since the HMAC secret is shared across all installations of the same app. No `api_secret_key` leak, token theft, or TLS interception is required — the attacker uses their *own* legitimately received, properly signed webhook and merely edits unauthenticated headers before forwarding it.

### Recommendation
Bind the shop/topic/webhook identity into the signed content rather than trusting bare headers. At minimum, `Webhooks::Registry.process` (or `HmacValidator`) should cross-check `request.shop` against an out-of-band trusted source (e.g., verify the shop is a currently-installed/known tenant via a server-side lookup keyed by a value that *is* covered by the signature, or use topic-specific signed payload fields), or `to_signable_string` should incorporate the canonical Shopify HMAC scheme's full signed payload/headers where available so that spoofing the `shop-domain` header invalidates the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on Shop A (their own store) and subscribes to any webhook topic.
2. Shopify delivers a webhook to the app's endpoint with body `B`, and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — the same `api_secret_key` is used for every shop that installed this app.
3. Attacker captures `(B, H)` and replays a new HTTP request to the same webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `Webhooks::Request.new` parses these headers (`lib/shopify_api/webhooks/request.rb:45-63`); `request.shop` now returns `victim-shop.myshopify.com` while `to_signable_string` still returns `B`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B) == H` — validation passes (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
6. `Registry.process` dispatches `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` to the host app's handler (`lib/shopify_api/webhooks/registry.rb:198-199`), which believes this is a genuine event from the victim shop, despite the payload/topic actually originating from the attacker's own shop.

### Citations

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
