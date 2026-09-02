This confirms the finding: `WebhookMetadata` passed to the app's `handle` callback carries `shop` — the identity field the app uses to attribute the webhook to a tenant — and that field is sourced directly from the `shop-domain` header, which is never part of the signed bytes.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are unauthenticated header values not covered by the HMAC, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the HMAC matches the body bytes; it never authenticates the `shop`, `topic`, `webhook_id`, or `api_version` values, which are read straight from attacker-controllable HTTP headers [2](#0-1) . `Registry.process` uses this unauthenticated `request.shop` to build the `WebhookMetadata` that is handed to the app's handler as the tenant identity [3](#0-2)  and `WebhookMetadata` defines `shop` as a plain, unauthenticated field passed to `WebhookHandler#handle` [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header value == shop cryptographically bound into the HMAC-signed bytes`. In this gem it does not — `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac` [5](#0-4) , and for `Webhooks::Request` the signable string is exactly the raw body, excluding all headers [1](#0-0) .

Every app built on this library that shares one `api_secret_key` across all installations (the normal, single-tenant-secret-multi-shop-app model) computes webhook HMACs with the same secret regardless of which shop the webhook is for. Because the shop identity is carried outside the signed payload, any party that can obtain one valid `(body, hmac)` pair for that shared secret — e.g., by installing the app on their own store and receiving a legitimate webhook — can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers. `Registry.process` will accept it, since `Utils::HmacValidator.validate(request)` only re-derives the signature from the body [3](#0-2) , and will dispatch to the handler with `WebhookMetadata.new(shop: request.shop, ...)` carrying the forged shop domain.

This breaks the intended equality: `authenticated payload attribution == shop the app subsequently acts on`. It matches the requested bug class directly: a field (`shop`) acted upon by downstream logic but not covered by the HMAC.

### Impact Explanation
This is a cross-tenant integrity issue: an unprivileged party who is merely a legitimate user of the app on their own shop can cause the app to process webhook events under another shop's identity, since the handler receives no cryptographic assurance that `shop` in `WebhookMetadata` matches the shop that actually produced the signed body. Depending on the host app's handler logic (order sync, redact handling, feature toggles, uninstall/redact triggers, billing state, etc.), this enables spoofed cross-tenant events without needing the victim's or even the app's `client_secret`.

### Likelihood Explanation
Exploitability requires only: (1) the ability to obtain one valid `(body, hmac)` pair signed with the app's shared secret — trivially available to anyone who installs the app on their own store and lets it deliver a real webhook, and (2) the ability to POST directly to the app's public webhook endpoint with custom headers, which any internet client can do since these endpoints are plain public HTTP(S) receivers with no other transport-level authentication enforced by this gem. No secrets, tokens, or privileged access are required.

### Recommendation
Bind the tenant/topic identity into the signed material instead of trusting headers post hoc: include `shop`, `topic`, and `webhook_id` in `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them, e.g. requiring the app to independently verify `shop` against a known/installed-shop list before trusting `WebhookMetadata#shop`), and document clearly that host apps must not treat the `shop` field as authenticated without such a check.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; the app registers webhooks and the attacker's own server (or a sniffing proxy) captures a legitimate webhook delivery, e.g. `orders/create` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker crafts a new HTTP POST to the app's real webhook endpoint with the same body `B` and the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` parses headers/body normally [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and finds it matches `H` [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [8](#0-7) , causing the app to act on attacker-controlled data attributed to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
