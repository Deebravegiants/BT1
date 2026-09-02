### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`/`api_version`/`webhook_id`) values are read from separate, unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body only and then passes the header-derived `shop` straight into `WebhookMetadata` for the app's handler to trust, breaking the binding "shop authenticated == shop the handler acts on."

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined so that only `@raw_body` participates in the signable string: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers via `shopify_header`, entirely outside of what `to_signable_string` returns: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the HMAC matches `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.shop` (a header value that was never covered by that HMAC) to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The resulting `WebhookMetadata.shop` is exactly the tenant identifier that app handlers are expected to use to route data to the correct merchant record: [5](#0-4) 

Because the HMAC only binds `raw_body`, an unprivileged holder of one legitimate, correctly-signed webhook (for their own shop — trivial to obtain since anyone can install/uninstall a Shopify app on their own dev shop and receive real webhooks with a valid HMAC for a given body) can replay that exact `raw_body` + valid `hmac` to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because it never inspects the shop header, and `Registry.process` forwards the attacker-chosen `shop` value to the handler as if it were authentic. This is the classic "bytes verified vs. bytes parsed" gap: the bytes cryptographically verified (body) diverge from the bytes the handler relies on for tenant identity (`shop` header).

### Impact Explanation
This breaks the identity binding `shop authenticated == shop the handler acts on for a given webhook`, allowing cross-tenant confusion: a handler that uses `data.shop` to look up/store per-merchant records, revoke tokens, or trigger merchant-specific side effects can be made to act on behalf of a victim shop using attacker-controlled body content, all while passing signature verification. This matches the Critical "cross-tenant access" impact category, since it lets one tenant inject events attributed to another tenant into the app's own trusted webhook pipeline.

### Likelihood Explanation
Likelihood is high for any app that relies on `WebhookMetadata#shop` for authorization/routing decisions (the documented, intended usage of this struct) rather than independently re-verifying the shop against a known webhook subscription/id. The attacker needs only one legitimate valid `(body, hmac)` pair from a webhook delivered to their own shop (trivially obtainable by installing the app on a shop they control) and the ability to POST to the app's public webhook endpoint with modified headers — no access token, `client_secret`, or privileged account is required.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the value that is HMAC-verified, or otherwise cryptographically bind the shop header to the signed body before it is trusted in `Registry.process`/`WebhookMetadata`. At minimum, document that consuming apps must not trust `WebhookMetadata#shop` without cross-checking it against the shop associated with the specific `webhook_id`/subscription that was registered.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker replays an HTTP POST to the app's public webhook endpoint with the same body `B` and the same `Shopify-Hmac-Sha256: H`, but sets `Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally (no header is bound to the HMAC) — [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` — [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, despite the request never having been signed for that shop — [8](#0-7) .

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
