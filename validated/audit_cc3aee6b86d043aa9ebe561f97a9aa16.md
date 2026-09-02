This confirms the vulnerability chain. `WebhookMetadata.shop` (and `topic`, `api_version`, `webhook_id`) are populated directly from `request.shop` etc., which come from unauthenticated headers, while only `@raw_body` is signed by the HMAC.### Title
Webhook `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are not covered by the HMAC signature, allowing cross-tenant metadata forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose `to_signable_string` returns only the raw request body [1](#0-0) . `Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string [2](#0-1) . However, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers that are never part of the signed payload [3](#0-2) . `Registry.process` validates only the HMAC of the body and then trusts `request.topic` and `request.shop` to route and populate `WebhookMetadata` passed to the app's handler [4](#0-3) , and `WebhookMetadata.shop` is a plain, unauthenticated field consumed by the handler [5](#0-4) .

### Finding Description
The identity binding this feature is supposed to enforce is: `hmac == HMAC(secret, signed_content)` where `signed_content` should represent "this exact webhook event, for this exact shop and topic, came from Shopify." Instead, `signed_content` is only the raw JSON body, and the `shop`, `topic`, `webhook-id`, and `api-version` fields are read from mutable HTTP headers that are excluded from the signature computation. This breaks the equality `authenticated(body) == authenticated(shop, topic, ...)`: only the body is authenticated, while the shop/topic/webhook_id/api_version claims delivered alongside it are not.

Because `Context.api_secret_key` is shared across all shops/tenants that install the same app, any party who can obtain one genuine `(body, hmac)` pair for a webhook event (e.g., by receiving webhooks for their own — even legitimately installed, unprivileged — shop, or by any means where the raw body is observable) can replay that exact body+hmac pair to the app's webhook endpoint while substituting arbitrary values for `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers. `HmacValidator.validate` will still return `true`, because it never inspects those headers [6](#0-5) . `Registry.process` will then dispatch to the handler registered for the forged `topic`, and hand the app's handler a `WebhookMetadata` claiming an arbitrary, attacker-chosen `shop` value, with `body` content that legitimately came from a different shop (or a different topic) [7](#0-6) .

### Impact Explanation
This maps to the "Critical — cross-tenant access" impact category: an app that uses the `shop` field from `WebhookMetadata` to look up per-tenant state (sessions, database records, feature flags, GDPR redaction targets, etc.) can be tricked into applying data or actions intended for shop A to shop B, since the gem does not guarantee that the `shop` header was actually generated for the body it accompanies. Because `MANDATORY_TOPICS` includes GDPR-sensitive topics like `customers/redact` and `shop/redact` [8](#0-7) , forging the `topic` header on a replayed body could also cause a handler registered for a highly sensitive topic to run against unrelated data.

### Likelihood Explanation
Exploitation requires the attacker to already possess one valid `(body, hmac)` pair for the app's `api_secret_key` — for example, by being a legitimate but unprivileged merchant who installed the app and received genuine webhooks for their own store. No access to `api_secret_key`, access tokens, or the victim's credentials is required; only header manipulation on replay, since the gem itself performs no validation of `shop`, `topic`, `webhook-id`, or `api-version` against the signed content.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed content, or otherwise cryptographically bind them to the body before dispatch, so `HmacValidator.validate` fails if any of these fields are altered relative to what Shopify actually signed.

### Proof of Concept
1. App receives a genuine webhook for `attacker-shop.myshopify.com`, topic `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: customers/redact`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers unmodified [9](#0-8) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — it matches, since the body was untouched [10](#0-9) .
5. The handler registered for the forged topic executes with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, i.e., attacker-controlled body data is attributed to a shop the attacker does not control.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
