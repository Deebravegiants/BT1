### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) header is trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook-id`, and `api-version` values used to route and attribute the event are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then passes the header-derived `shop` straight into the handler's `WebhookMetadata`, so the binding "HMAC-authenticated request" == "shop the payload is attributed to" does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read directly from HTTP headers and are never included in the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body), and then forwards the *unauthenticated* `request.shop` header value into `WebhookMetadata` that is handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms only that `verifiable_query.to_signable_string` (the raw body) matches the HMAC — it has no visibility into headers at all: [4](#0-3) 

Because the app's webhook endpoint is a public internet-reachable URL (this is how Shopify itself delivers webhooks), any unprivileged internet user — including a legitimate merchant of the app who can capture one of their own genuine `(body, hmac)` pairs — can POST that same untouched body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with an arbitrary value. The HMAC still validates (it only covers the body, which is unmodified), but `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to whatever `shop` the attacker put in the header.

This is the direct analog of the reported bug class "a field acted on but not covered by the HMAC": the binding `hmac_verified(body) == true` is treated as if it also implies `shop_header == actual_owning_shop`, but those are two independent, unrelated facts.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (the documented, intended way to identify which tenant a webhook event belongs to) to route data updates, invalidate caches, revoke access, or otherwise act on a specific merchant's account will process an attacker-chosen shop identifier alongside data that did not originate from that shop's Shopify instance. This breaks per-tenant isolation — a cross-tenant confusion in the exact record the gem promises to have authenticated via HMAC. It maps to the Critical "cross-tenant access" impact category because the shop-scoping guarantee the HMAC check is supposed to provide is not actually provided for the `shop` field.

### Likelihood Explanation
The attack requires no credentials, secrets, or privileged access: the webhook endpoint is a normal public HTTP(S) endpoint reachable by anyone, and an attacker only needs to capture one legitimate `(raw_body, x-shopify-hmac-sha256)` pair — trivially obtainable by any merchant who has installed the app and can observe/replay their own webhook traffic (or via any interception of a single webhook delivery). No knowledge of `api_secret_key` or an access token is required to exploit the header/body mismatch itself.

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the signable content used for HMAC verification, or otherwise cryptographically bind them to the verified body (e.g., verify that the `shop` header matches an app-side expectation established during OAuth for that specific webhook subscription) before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC check and must not be used by host apps as a trust boundary without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (or otherwise observes one legitimate webhook delivery).
2. Shopify sends a legitimate webhook to the app's public callback URL with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Attacker replays this exact `(B, H)` pair directly to the same public endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `H` still matches `HMAC-SHA256(secret, B)`: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process `B`'s content as belonging to `victim-shop`, despite the event never having originated from or been authorized by that shop.

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
