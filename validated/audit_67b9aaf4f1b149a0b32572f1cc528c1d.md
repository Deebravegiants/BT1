### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then passes the unauthenticated `shop-domain` header straight to the handler as the trusted tenant identifier.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate`/`validate_signature` compute and compare the HMAC exclusively over that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all read directly from HTTP headers and are never part of the signed content [3](#0-2) .

`Registry.process` checks `Utils::HmacValidator.validate(request)` and, if it passes, immediately builds `WebhookMetadata` using `request.shop` — the unauthenticated header value — and hands it to the app's handler as the trusted tenant identifier [4](#0-3) .

Because `Context.api_secret_key` is a single, app-wide secret shared across every shop that installs the app (not a per-shop secret) [5](#0-4) , any merchant who installs the app receives real, validly-signed webhook deliveries (body + HMAC) for their own shop. Since the `shop-domain` header is outside the HMAC's scope, that same attacker can replay the identical body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` value. `HmacValidator.validate` still returns `true` because it only recomputes the HMAC over the untouched raw body [6](#0-5) , so `Registry.process` treats the forged domain as authentic and forwards it to the handler [4](#0-3) .

This is exactly the binding-break pattern flagged in the report: a field (`shop`) that is acted upon by the application (used as the tenant key for downstream processing) but not covered by the HMAC that is supposed to authenticate the whole request.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` (the documented, intended way to identify which tenant a webhook belongs to) as a lookup key for session/store data will process attacker-supplied webhook bodies under a victim shop's identity. This is a cross-tenant boundary violation: an unprivileged attacker (any merchant who can install the app) can inject data or trigger side effects (e.g. `orders/create`, `app/uninstalled`, or other topic handlers) that the host application believes originated from a different, victim shop, without needing any credentials belonging to that shop.

### Likelihood Explanation
High. Any developer/merchant can install the target app on their own store, capture one legitimate webhook delivery (body + HMAC + headers) for a registered topic, and immediately replay it with only the `x-shopify-shop-domain` header changed. No secret, token, or privileged access is required — only the general ability to install the app, which is available to any internet user for public apps.

### Recommendation
Do not treat `request.shop` as authenticated by the webhook HMAC. At minimum:
- Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values in the signable string that is HMAC-verified, mirroring how Shopify's own webhook signature is intended to bind the full delivery context, or
- Require callers/handlers to cross-check `request.shop` against a shop that is independently known to have an active session/installation before trusting it, and document that `shop-domain` is not cryptographically bound by `HmacValidator.validate`.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook for a registered topic (e.g. `orders/create`). Capture the raw HTTP request: body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Resend the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com`; keep body `B` and HMAC header `H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body as before [7](#0-6) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (== `B`, unchanged) and matches `H`, so validation passes [8](#0-7) .
4. `handler.handle` receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes attacker-controlled body `B` under the victim's tenant identity [9](#0-8) .

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

**File:** lib/shopify_api/context.rb (L1-20)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  class Context
    extend T::Sig

    @api_key = T.let("", String)
    @api_secret_key = T.let("", String)
    @api_version = T.let("", String)
    @api_host = T.let(nil, T.nilable(String))
    @scope = T.let(Auth::AuthScopes.new, Auth::AuthScopes)
    @is_private = T.let(false, T::Boolean)
    @private_shop = T.let(nil, T.nilable(String))
    @is_embedded = T.let(true, T::Boolean)
    # Logger can either be a Logger or an ActiveSupport::BroadcastLogger, which is new in Rails 7.1.0. To avoid adding a
    # dependency Active Support >= 7.1.0, we go with T.untyped
    @logger = T.let(::Logger.new($stdout), T.untyped)
    @log_level = T.let(:info, Symbol)
    @notified_missing_resources_folder = T.let({}, T::Hash[String, T::Boolean])
```
