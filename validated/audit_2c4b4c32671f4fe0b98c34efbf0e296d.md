### Title
Webhook `shop`/`topic` identity is trusted from unauthenticated HTTP headers while the HMAC only signs the raw body, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC computed only over the raw request body [1](#0-0) , then dispatches to the app's handler using the `shop` and `topic` values taken directly from the `X-Shopify-Shop-Domain` / `X-Shopify-Topic` HTTP headers, which are never included in the signed content [2](#0-1) . This is the same bug class as the Sherlock M-3 finding: a value (there, a fee percentage; here, the tenant/shop identity) is used by downstream logic without being bound into the value that was actually cryptographically verified.

### Finding Description
`Request#hmac` returns the hex-decoded `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body` [2](#0-1) . `Utils::HmacValidator.validate` computes `HMAC-SHA256(client_secret, to_signable_string)` and compares it to the header-supplied value [3](#0-2) . Crucially, the `shop` and `topic` getters read straight from headers and are **not** part of `to_signable_string`: `shop` returns `shopify_header("shop-domain")` and `topic` returns `shopify_header("topic")` [4](#0-3) .

`Registry.process` only calls `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop` and `request.topic` to build the `WebhookMetadata` passed to the app's handler [1](#0-0) . `WebhookMetadata.shop` is a plain `String` field with no further verification [5](#0-4) .

The identity binding that should hold is:
`authenticated_shop (i.e., the shop whose install/HMAC-secret produced the signed bytes) == shop delivered to WebhookHandler#handle`

What the code actually enforces is:
`HMAC(client_secret, raw_body) == header_hmac` AND (separately, unauthenticated) `shop = header_shop-domain`

Because a single Shopify app has one `client_secret` shared across every shop that installs it, any shop that has installed the app can capture a **legitimate** `(raw_body, hmac)` pair sent to its own webhook endpoint (e.g. from any topic it can trigger, such as `app/uninstalled`, `orders/create`, etc.) and replay that exact body+HMAC to the app's webhook endpoint while substituting a different value in the `X-Shopify-Shop-Domain` header. Since `shop` is read from the header and never covered by the HMAC, `Registry.process` will pass HMAC validation and call the handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain, alongside body content the attacker controls (their own store's data).

### Impact Explanation
This crosses a tenant boundary inside the gem's own webhook-processing helper: an app relying on `ShopifyAPI::Webhooks::Registry.process`/`Request#shop` to route or attribute per-tenant side effects (e.g., mark a shop's subscription cancelled, update per-shop state, trigger data deletion flows for GDPR topics like `customers/redact`) can be made to apply another tenant's operation to a shop the attacker does not own — a cross-tenant access impact, matching the Critical bucket ("cross-tenant access") in the impact taxonomy for this analysis. The severity is amplified because mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) are handled by the exact same unauthenticated-shop code path [6](#0-5) .

### Likelihood Explanation
Exploitation requires only that the attacker control one shop that has installed the target app (an "unprivileged internet user" with respect to any other tenant of the app) — no access to the app's `client_secret`, access tokens, or other shops' credentials is needed. The attacker legitimately receives HMAC-signed webhooks for their own shop and only needs to replay the body/HMAC with a forged `shop-domain` header to a publicly reachable webhook endpoint. This is a realistic, low-effort attack path fully reachable through this gem's documented `Registry.process` API, not dependent on the host app ignoring documented behavior — the gem itself never binds `shop`/`topic` into the verified signature.

### Recommendation
Bind the `shop` (and ideally `topic`) header values into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the verified payload (e.g., include shop/topic in the signable string as Shopify's own webhook signature scheme evolves to support, or require the caller to independently verify the header `shop` against a known/installed-shop list before trusting it for tenant-scoped operations). At minimum, document prominently that `Request#shop`/`Request#topic` are not covered by the HMAC and must not be used as the sole tenant identity for authorization-sensitive operations.

### Proof of Concept
1. App has installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both using the same app `client_secret`.
2. Attacker's shop `attacker-shop.myshopify.com` triggers a real webhook (e.g. `orders/create`); Shopify sends:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-raw-body>`
   - Body: `<raw_body>`
3. Attacker replays the exact same `<raw_body>` and the same valid `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` computes `HmacValidator.validate(request)` over `raw_body` only — validation succeeds (the HMAC value was never tied to the shop header) [7](#0-6) .
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker-controlled order data>, ...)` [8](#0-7) , causing the app to process attacker-controlled data as belonging to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
