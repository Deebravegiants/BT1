Confirmed: `ShopifyAPI::Webhooks::Request#shop` in [1](#0-0)  reads the `shop` value straight from the `x-shopify-shop-domain` HTTP header, while `to_signable_string` (the content the HMAC actually covers) is only the raw body [2](#0-1) . `Registry.process` verifies only that HMAC before dispatching, then hands the handler a `WebhookMetadata` built from `request.shop` [3](#0-2) . `HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` and compares it with `verifiable_query.hmac` [4](#0-3) , so the shop-domain header is never part of the signed material.

### Title
Webhook `shop` identity is taken from an HTTP header that is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The gem's webhook verification only authenticates the request body via HMAC-SHA256; the `shop` attribute exposed to webhook handlers is read from the `x-shopify-shop-domain` header, which is completely outside the signed data. Anyone who can produce one genuine, validly-signed webhook body (e.g., by operating their own store that has installed the app, which triggers Shopify to send real webhooks signed with the app's shared `api_secret_key`) can replay that same body/HMAC pair while substituting an arbitrary `shop-domain` header value. The signature still validates because it never covered the shop identity, letting the attacker have the library report an attacker-chosen victim shop.

### Finding Description
`Webhooks::Request#shop` derives its value entirely from `shopify_header("shop-domain")` [1](#0-0) , an unauthenticated field parsed straight from client-supplied headers [5](#0-4) . The HMAC that the library validates is computed only over `to_signable_string`, which returns `@raw_body` and nothing else [2](#0-1) . `Registry.process` calls `Utils::HmacValidator.validate(request)` and, on success, immediately builds `WebhookMetadata` from `request.shop` and hands it to the registered handler [3](#0-2) , so the identity binding the report describes — "a field acted on but not covered by the HMAC" — is broken here: `shop` is acted on (returned as the trusted tenant identifier) but `shop ∉ to_signable_string`.

This differs from the OAuth callback path, where `AuthQuery#to_signable_string` explicitly folds `shop` into the signed content alongside `code`, `host`, `state`, and `timestamp` [6](#0-5) , correctly binding the shop identity to the HMAC. No equivalent binding exists for webhooks.

Since all webhooks for an app are signed with the same shared `Context.api_secret_key` regardless of which shop triggered them [7](#0-6) , a signature that is valid for one tenant's payload is equally valid for the same bytes presented as coming from any other tenant — the HMAC proves only "signed by this app's secret," not "originated from shop X."

### Impact Explanation
This breaks the tenant identity equality `authenticated_shop == claimed_shop` that host applications rely on `WebhookMetadata#shop` to enforce. An attacker who installs the app on their own (unprivileged) store receives genuinely signed webhooks for their own data. By replaying that exact signed body with a forged `x-shopify-shop-domain` header naming a victim shop, the library will report the payload as belonging to the victim tenant while passing HMAC validation — a cross-tenant confusion at the trust boundary the gem itself is responsible for establishing.

### Likelihood Explanation
Reachable by any user capable of installing the app on a store they control (no privileged credentials, tokens, or `api_secret_key` knowledge required) and capable of sending an arbitrary HTTP request to the app's public webhook endpoint with attacker-controlled headers — both are standard, unprivileged capabilities for any Shopify merchant/app installer.

### Recommendation
Bind the shop identity into the signed material, mirroring the OAuth `AuthQuery` pattern: include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in `to_signable_string`, or otherwise cryptographically bind them to the body before computing/verifying the HMAC, so `Registry.process` cannot report a `shop` value that was not part of what was actually authenticated.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger a webhook event so Shopify sends a legitimately HMAC-signed request, e.g. `raw_body = '{"id":1}'`, `x-shopify-hmac-sha256 = <valid HMAC over raw_body with api_secret_key>`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture this exact `raw_body` and `x-shopify-hmac-sha256` value.
3. Replay the same body and HMAC header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `raw_body` [2](#0-1)  — validation succeeds because the shop header was never part of the signed content.
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the data actually originated from the attacker's own store [8](#0-7) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L16-21)
```ruby
          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
