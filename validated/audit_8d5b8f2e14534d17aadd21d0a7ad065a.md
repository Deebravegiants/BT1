### Title
Webhook shop-domain, topic, and webhook-id headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by HMAC-verifying the raw request body via `Utils::HmacValidator.validate`, which calls `request.to_signable_string`. In `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . These header-derived fields are then trusted and forwarded directly into `WebhookMetadata` and the app's handler [3](#0-2) , without any of them being bound to the HMAC that "authenticates" the request.

### Finding Description
The identity binding that should hold is: `shop header == shop that the HMAC-signed payload actually originated from`. Because `to_signable_string` signs only the body, this equality is never checked — the HMAC only proves "this body byte-sequence was produced with knowledge of `api_secret_key`," it says nothing about which header set (topic/shop-domain/webhook-id/api-version) accompanies that body.

`api_secret_key` is a single, app-level secret shared across every shop that has the app installed (it is not per-shop) [4](#0-3) . Consequently, any party who can get one genuine, validly-signed webhook body from the app (e.g., by installing the app on their own store and receiving a real webhook, which is something an ordinary merchant/attacker can do without any special credentials) possesses a `(raw_body, hmac)` pair that will pass `HmacValidator.validate` regardless of which `shop-domain`, `topic`, or `webhook-id` header is attached to a replayed request, since none of these are part of the signed content.

`Registry.process` performs no additional binding check between the validated body and the header-derived `shop`/`topic`: it validates HMAC, looks up the handler purely by `request.topic` (attacker-controlled header), and constructs `WebhookMetadata` using `request.shop` (also attacker-controlled) [3](#0-2) . If the host application's handler uses `data.shop` to select which merchant's session/data to update (the documented, intended usage pattern for `WebhookHandler#handle`) [5](#0-4) , an attacker can replay a self-obtained, validly-signed webhook body while substituting an arbitrary victim `shop-domain` header (and/or `topic`/`webhook-id` header) and have the gem report it as authentic, causing the handler to act on a different tenant's data than the one that actually produced the signed content.

### Impact Explanation
This breaks the binding between the HMAC-authenticated bytes and the tenant/topic the app believes the webhook is for, enabling cross-tenant confusion: a party who legitimately receives one signed webhook (e.g., from their own store) can forge the accompanying `shop-domain`/`topic` metadata to impersonate a different merchant or a different event type, all while passing `HmacValidator.validate`. This matches the Critical "cross-tenant access" impact category, since the merchant identity (`shop`) consumed by the host app's handler is not actually authenticated by this gem, only the raw body is.

### Likelihood Explanation
Likelihood is meaningful: obtaining one genuine `(body, hmac)` pair requires no privileged credentials — installing a free/dev app instance and receiving any real webhook suffices, since `api_secret_key` is shared across all installs of the same app. From there, forging the `shop-domain`/`topic`/`webhook-id` headers on a replayed HTTP request is trivial (any internet-reachable webhook endpoint accepts attacker-supplied headers). The only constraint is that the replayed body's *content* must still make sense to the target handler (e.g., an empty-body or generic-topic webhook is easiest to abuse), which is a plausible scenario for topics with minimal or predictable payloads.

### Recommendation
Bind the header-derived identity fields into the HMAC-verified signable content, or otherwise cryptographically/contextually tie `shop`, `topic`, and `webhook_id` to the verified body before trusting them — e.g., have `to_signable_string` incorporate the shop domain/topic, or require the caller to independently confirm `request.shop` corresponds to a shop with an active, known session/installation before dispatching to handlers, rather than trusting the raw header value outright.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker-shop.myshopify.com`) and receives one real webhook, e.g. topic `X`, body `{}`, with a valid `x-shopify-hmac-sha256` value computed by Shopify using the app's `api_secret_key`.
2. Attacker replays this exact `raw_body` (`"{}"`) to the app's webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: <any topic the attacker wants the handler to fire for>`
   - keeps the original, still-valid `x-shopify-hmac-sha256`.
3. `Request#initialize` accepts the headers (only checks presence, not correlation) [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only compares the HMAC of `raw_body` (`"{}"`), unaffected by the header substitution [7](#0-6) .
4. The handler is invoked with `WebhookMetadata(topic: <attacker-chosen>, shop: "victim-shop.myshopify.com", body: {}, ...)` [8](#0-7) , causing the host app to act as though `victim-shop` sent this webhook, even though the signed bytes originated from the attacker's own shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
