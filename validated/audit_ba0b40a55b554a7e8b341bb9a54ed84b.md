### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) fields are trusted for tenant identification without being covered by the HMAC signature, enabling cross-tenant webhook impersonation - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0)  while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC over that body-only signable string, then immediately trusts `request.shop`/`request.topic` to dispatch the payload to the merchant-specific handler [3](#0-2) . Since every shop installed on the same app shares one `api_secret_key`, the signature proves only "this body was signed by our app's secret," not "this body belongs to shop X." The `shop` header is a field acted on (tenant routing) but not covered by the HMAC — exactly the identity-binding break the analog class targets.

### Finding Description
The equality that should hold is:

`shop asserted by request.shop == shop cryptographically bound by the HMAC`

In `Request#initialize`, headers (`x-shopify-shop-domain`/`shopify-shop-domain`, topic, webhook-id, api-version) are normalized and stored, and are exposed via plain accessors [4](#0-3) [5](#0-4) . But `to_signable_string`, the only material fed into the HMAC check, is just `@raw_body` [6](#0-5) .

`Utils::HmacValidator.validate` computes `HMAC(api_secret_key, to_signable_string)` and constant-time-compares it to the `hmac` header [7](#0-6) . This only proves the *body* bytes were signed by the app's secret — it says nothing about which shop, topic, webhook id, or api version accompanied that body.

`Registry.process` then does:
```
raise ... unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

Because `api_secret_key` is the same for every merchant shop of a given app, once an attacker who controls (or has previously received) any single valid `(raw_body, hmac)` pair for their own shop, they can replay that exact body/hmac pair while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with a different shop's domain or a different topic/id. The signature still validates because it never covered those fields. The host application's handler then processes the forged `WebhookMetadata` believing it originates from the spoofed shop/topic/webhook id.

Before the request: `request.shop` is attacker-controlled and unauthenticated.
After `HmacValidator.validate` passes: `request.shop` is still attacker-controlled and unauthenticated — the validation state did not change with respect to that field, yet the caller (`Registry.process`) treats the request as fully authenticated for `shop` and `topic` when building `WebhookMetadata`.

### Impact Explanation
This breaks tenant isolation: a webhook payload can be attributed to an arbitrary shop domain or topic without possessing the app's `client_secret`/`api_secret_key`. Any host application relying on `WebhookMetadata#shop` to select the tenant/session to update, persist, or act on receives cross-tenant data driven by attacker-controlled headers. This matches the Critical "cross-tenant access" impact category, since the gem itself performs no binding between the authenticated bytes (body) and the trusted identity field (`shop`).

### Likelihood Explanation
The attacker only needs to have obtained one legitimately-signed `(raw_body, hmac)` pair for the app (e.g., as an app-installing merchant themselves, or by observing/replaying a captured webhook delivery, since webhook endpoints are typically public HTTP endpoints without additional secrecy on headers). No possession of `api_secret_key` or an access token is required, satisfying the "unprivileged internet user" constraint. The replay/header-substitution mechanics are trivial once such a pair is obtained.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC computation, or otherwise cryptographically bind them (e.g., HMAC over `shop|topic|webhook_id|raw_body`) so `to_signable_string` in `lib/shopify_api/webhooks/request.rb` reflects everything `Registry.process` subsequently trusts. Alternatively, document and enforce that host applications must independently verify `shop` against their own session/tenant store before acting on `WebhookMetadata`, and reject `Registry.process` from exposing `shop`/`topic` as trusted output of HMAC validation.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives (or triggers) a webhook delivery with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC(api_secret_key, B)`.
2. Attacker replays the same `B` and `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, B) == H`, unaffected by the spoofed `shop` header [8](#0-7) .
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and dispatched to the app's handler, which now processes attacker-controlled data as if it belongs to the victim shop [9](#0-8) .

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
