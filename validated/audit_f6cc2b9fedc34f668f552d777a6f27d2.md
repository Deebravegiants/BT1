This confirms the identity binding break: the webhook's `shop` field (and `topic`/`webhook_id`) are read from HTTP headers (`shopify-shop-domain`, etc.) which are **not part of the HMAC-signed payload** — the HMAC in `Utils::HmacValidator.validate` only signs/verifies `to_signable_string`, which for `Webhooks::Request` returns just `@raw_body` [1](#0-0) . Since the app's `api_secret_key` (client secret) is shared across every merchant that installs the app, any tenant that installs the app can obtain a validly-HMAC'd webhook body for their own shop, then replay it to the app's webhook endpoint with a forged `shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` will pass because it only checks the body signature [2](#0-1) , and `Registry.process` then dispatches the handler using the attacker-controlled `request.shop` [3](#0-2) .

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are validated as HMAC-authentic while being unauthenticated header values - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#to_signable_string` returns only the raw body, so the HMAC signature Shopify computes for a webhook covers the JSON payload alone, not the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers. `Webhooks::Registry.process` treats a passing `HmacValidator.validate(request)` check as proof the *entire request*, including `request.shop`, is authentic and trustworthy, then hands that shop value straight to the host application's handler.

### Finding Description
The equality the code implicitly (and incorrectly) assumes is:
`HMAC-verified(raw_body) == HMAC-verified(shop, topic, webhook_id, raw_body)`

In reality:
- `hmac` is derived from `shopify-hmac-sha256` header [4](#0-3) .
- `to_signable_string` (the bytes actually checked) is `@raw_body` only [1](#0-0) .
- `shop`, `topic`, and `webhook_id` are parsed straight from separate, unsigned headers [5](#0-4) .

Because the app's `api_secret_key` is a single shared secret across every merchant/shop that has installed the app (it is not per-shop), a webhook body legitimately signed by Shopify for tenant A's shop produces an HMAC that is also "valid" if replayed with tenant A pretending the `shopify-shop-domain` header is tenant B's shop. `Registry.process` only re-checks the body HMAC via `Utils::HmacValidator.validate(request)` [6](#0-5)  and then unconditionally forwards `request.shop` to the handler as trusted tenant identity [7](#0-6) . Nothing in this gem binds the `shop` header to the signed body.

### Impact Explanation
This is a cross-tenant confusion/attribution vulnerability: a malicious but legitimate installer of the app (attacker controls shop A) can produce genuinely HMAC-valid webhook requests (since Shopify signs their own shop's webhooks with the shared app secret) and then relay/replay them to the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim's shop domain (shop B). The host application, trusting `WebhookMetadata#shop` as authenticated, will process the payload as if it originated from and pertains to shop B — potentially triggering data writes, cache/session invalidation, order/inventory updates, or uninstall/GDPR handling logic keyed on the wrong tenant. This crosses the tenant boundary this gem is meant to enforce.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker must be an actual (even free/trial) installer of the target app in order to receive a validly-signed webhook body under the shared secret, and must be able to reach the app's public webhook endpoint directly (bypassing Shopify's own delivery, e.g., via curl/replay). No access token, `api_secret_key`, or privileged account is required beyond ordinary app installation, which is attacker-obtainable.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values to the HMAC-verified content instead of trusting bare headers: either require the webhook payload itself to include/attest the shop domain and compare it to the header, or include the relevant headers as part of the canonical string passed to `to_signable_string` so they are covered by the HMAC verification, and reject the request if they don't match what Shopify actually included in the signed payload.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, becoming a legitimate holder of the shared `api_secret_key`-derived signatures for their own shop's webhooks.
2. Shopify sends a legitimate webhook to the app's endpoint with headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid HMAC of raw_body>`, and some `raw_body`.
3. Attacker captures this request and re-sends it directly to the app's webhook endpoint, changing only `shopify-shop-domain` to `victim-shop.myshopify.com` (and, if desired, editing `topic`/`webhook_id`), leaving `raw_body` and `shopify-hmac-sha256` untouched.
4. `Webhooks::Request.new` accepts it (all required headers present) [8](#0-7) ; `HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against `hmac` [9](#0-8) .
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , causing the host app to act on `victim-shop`'s tenant data/state using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
