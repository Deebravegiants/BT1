### Title
Webhook shop-domain identity is unauthenticated by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw HTTP body, while the `shop` (tenant identity), `topic`, `api_version`, and `webhook_id` fields are read directly from unauthenticated HTTP headers and passed on to the host app's handler as trusted tenant context. This breaks the intended binding `hmac_verified_bytes == tenant_identity_bytes`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Registry.process` validates only that signature against this raw body: [2](#0-1) , then immediately forwards `request.shop` (sourced from the `shopify-shop-domain`/`x-shopify-shop-domain` header, never covered by the HMAC) into `WebhookMetadata` and to the handler: [3](#0-2) . The `shop` accessor itself is defined purely as a header read with no cryptographic tie to the body: [4](#0-3) .

`HmacValidator.validate` computes the signature using the app's single, shop-independent `Context.api_secret_key` (the app's `client_secret`), which is identical for every shop that installs the app: [5](#0-4) . Because the signature is a function only of `(raw_body, api_secret_key)` and not of `shop`, any two webhooks with identical bodies (e.g., identical JSON payloads, which commonly occurs for boilerplate/system topics such as `shop/redact`, `customers/redact`, `app/uninstalled`, or any payload an attacker can trigger on their own store to get a matching body) produce the exact same valid HMAC regardless of which shop the request claims to be from.

This is the same class of bug as the reported finding: a value that is *acted upon as an identity/tenant discriminator* (there: `bathHouse`/pair identity for `rebalance`; here: `shop` for per-tenant webhook processing) is not actually bound by the control meant to authenticate the caller (there: `onlyPair`/admin-controlled trust; here: the HMAC signature). The equality that should hold is:
`shop_authenticated_by_hmac == shop_used_by_handler`
but in reality:
`shop_used_by_handler = header value (uncovered by hmac) ≠ shop implied by hmac (none, since hmac covers only body)`

### Impact Explanation
An unprivileged holder of a legitimate installation (any merchant/tenant of the app, i.e., an "unprivileged internet user" relative to any other tenant) can capture a real, validly-signed webhook delivered to their own endpoint for their own shop, then replay the identical `raw_body`+`hmac` while substituting the `shopify-shop-domain` header to name a victim shop. `Registry.process` will pass HMAC validation and dispatch the handler with `WebhookMetadata#shop` set to the victim shop, causing the host application to attribute/act on that payload as if it originated from the victim tenant — a cross-tenant confusion/impersonation that can lead to cross-tenant data writes, redaction actions, or state changes scoped to the wrong shop, depending on how the host app's handler uses `data.shop`. This matches the Critical impact category "cross-tenant access."

### Likelihood Explanation
Any app merchant already has one authenticated relationship with the app (their own shop) and can trivially receive/capture their own real webhook deliveries (body + valid signature) without needing the app's `client_secret`, an access token, or any privileged access. Forging only the shop-domain header requires no cryptographic material at all beyond what any tenant can already observe on their own traffic. The main constraint is finding/producing a webhook payload with content the attacker doesn't control (topic and body semantics), but system/boilerplate topics with predictable/empty bodies (e.g., `{}` in this repo's own webhook tests) make this straightforward.

### Recommendation
Bind the tenant identity into the verified signature material, or independently validate it: include `shop` (and ideally `topic`/`webhook_id`) in the value passed to `to_signable_string`/HMAC computation, or require the host app to cross-check `shop` against a shop that is already known/authorized (e.g., matching against a known session or previously-registered shop) before dispatching to `handler.handle`. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically authenticated and must not be trusted for tenant scoping without additional verification.

### Proof of Concept
1. App has one shared `client_secret` (`ShopifyAPI::Context.api_secret_key`) as shown by `HmacValidator.validate_signature`, `Context.api_secret_key` used identically for all shops: [6](#0-5) .
2. Attacker (merchant of `attacker-shop.myshopify.com`) receives a real webhook at their own endpoint with body `{}` and header `x-shopify-hmac-sha256: <valid-hmac-of-{}>`.
3. Attacker resends the identical body/hmac to the app's shared webhook endpoint, changing only `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Request.new` builds a request object where `shop` == `"victim-shop.myshopify.com"` and `hmac` is the same valid value: [7](#0-6) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body signature: [8](#0-7) .
6. The host app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the request never actually originated from Shopify on behalf of that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
