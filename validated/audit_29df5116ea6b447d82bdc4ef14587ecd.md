This confirms the finding: `WebhookMetadata.shop` (and `topic`/`webhook_id`/`api_version`) are populated directly from HTTP headers, while `Utils::HmacValidator.validate` only verifies `request.to_signable_string`, which returns `@raw_body` — the headers are never part of the signed content.### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`/`api_version`) values that are handed to the app's webhook handler are read straight from unauthenticated HTTP headers, which are never included in the HMAC-signed content. This breaks the identity binding `authenticated-shop == HMAC-covered-shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers (`x-shopify-shop-domain`, etc.), completely separate from the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string`, i.e. only the raw body bytes: [3](#0-2) 

`Registry.process` checks the HMAC, then immediately builds `WebhookMetadata` (which is passed to the app-defined handler) using `request.shop` taken from the unauthenticated header: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no further binding to the HMAC: [5](#0-4) 

Because the HMAC only proves "this exact body was signed with the app's secret at some point," and does not prove which shop or topic that body belongs to, an attacker who can obtain one valid `(raw_body, hmac)` pair (e.g., by installing the app on a shop they control, or from any leaked/observed webhook delivery) can replay that exact body+HMAC to the app's public webhook endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` header values. `Utils::HmacValidator.validate` will still pass because it never inspects the headers, and `Registry.process` will invoke the app's handler with attacker-chosen `shop`/`topic`/`webhook_id` values alongside the replayed body content.

This is the direct analog of the reported bug class: a field that is acted upon by downstream logic (`shop`, used by the handler to attribute the webhook to a tenant) is not covered by the same integrity check (`HMAC`) that is used to establish trust in the request as a whole — exactly the "field acted on but not covered by the HMAC" pattern called out in the rules.

### Impact Explanation
Any application built on this gem's documented webhook API implicitly trusts `WebhookMetadata#shop` as the authenticated tenant identifier for the webhook (this is exactly how the gem's own docs instruct apps to use it — `data.shop` — for tenant attribution). By forging the `shop` header on a replayed, still-validly-signed body, an attacker can make the app process webhook data under an arbitrary victim shop's identity. Depending on how the host app uses `data.shop` (e.g., to select which merchant's stored access token/session to act on, or to write data into that merchant's records), this enables cross-tenant data/actions to be misattributed — a cross-tenant access condition, which is explicitly listed as a Critical-impact category.

### Likelihood Explanation
Medium-to-High: the attacker only needs one legitimately signed `(body, hmac)` pair, which is trivially obtainable by installing the target app on any shop the attacker controls (a free/dev store) and capturing the resulting webhook delivery. No knowledge of `api_secret_key` is required — the header spoofing works purely because the header fields are outside the HMAC's protected scope. This does not require a privileged account, TLS interception, or social engineering, and works entirely through this gem's own documented `Registry.process`/`Request` API.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-verified content instead of trusting raw headers independently, or otherwise cryptographically or contextually verify that the claimed `shop` header corresponds to a shop that is actually expected to be sending this specific signed body (for example, incorporate these header values into the string that is HMAC-verified, similar to how `AuthQuery#to_signable_string` binds `shop`/`host`/`code` together for OAuth callbacks). At minimum, document loudly and enforce in the gem that `WebhookMetadata#shop` must never be used for authorization/tenant-selection decisions without an independent, out-of-band correlation (e.g., only accepting webhooks for shops for which the app already holds an active, previously-obtained access token, and verifying idempotency/webhook_id uniqueness per that shop).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a store they control).
2. Shopify sends a legitimate webhook, e.g. `orders/create`, to the app's endpoint with:
   - Body: `{"id": 1, ...}` 
   - Header `x-shopify-hmac-sha256`: valid HMAC-SHA256 of the raw body using the app's `client_secret`
   - Header `x-shopify-shop-domain`: `attacker-shop.myshopify.com`
3. Attacker captures this exact `(raw_body, hmac_header)` pair.
4. Attacker sends a new HTTP POST to the app's webhook endpoint with the **same** `raw_body` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a fresh `x-shopify-webhook-id` to bypass idempotency checks).
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC — the shop header is never examined.
6. `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's own order data>, ...)`, causing the host application to process attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

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
