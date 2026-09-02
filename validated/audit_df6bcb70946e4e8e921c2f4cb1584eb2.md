### Title
Webhook `shop-domain` and `topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content only from the raw request body, while the `shop`, `topic`, and `webhook_id` fields that identify *which tenant and event* the payload belongs to are taken directly from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC and then dispatches the handler using these unauthenticated header values, so the "shop" that gets bound to the processed data is never actually verified by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which internally calls `verifiable_query.to_signable_string`, i.e. only the body — and then immediately builds `WebhookMetadata` (the object passed to the app's business logic) straight from the unauthenticated `request.shop`/`request.topic`/`request.webhook_id`: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and the app's `api_secret_key`: [4](#0-3) 

`WebhookMetadata` carries `shop` as a plain, unauthenticated `String` field that handlers rely on to know which merchant the event is for: [5](#0-4) 

**Identity binding broken (as an equality):**
`shop authenticated by HMAC` ≠ `shop delivered to the handler as tenant identity`.

The HMAC only proves "this body was signed with `api_secret_key`" — it says nothing about which shop or topic it belongs to. Since a single app has one `client_secret`/`api_secret_key` shared across *all* installs (all merchants), anyone who can capture one valid `(raw_body, hmac)` pair for the app — e.g., a merchant/developer who installed the app on their own store and can read the raw webhook body/HMAC they received — can replay that exact body+HMAC against the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a different (victim) shop. `HmacValidator.validate` still returns `true` because it never inspects those headers, and `Registry.process` will dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who legitimately controls the HMAC secret's *scope* (any single merchant install of the multi-tenant app) can make the host application process replayed payloads under a different merchant's `shop` identity, since `shop` is not bound into the signed material. Depending on how the host application keys its data/session lookups off `WebhookMetadata#shop` (this is documented/intended usage of this gem's API), this can lead to cross-tenant data corruption or disclosure — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus one legitimately obtained `(body, hmac)` sample from any store using the same app (trivial for an attacker who installs the target app on their own store, a normal, unprivileged action) — no `api_secret_key`, access token, or privileged account needed. No TLS interception or credential theft is required; only header spoofing on the replayed HTTP request.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` into the HMAC-signable material (or otherwise cryptographically verify them, e.g. only trust `shop`/`topic` values that are independently confirmed against Shopify, or include them in `to_signable_string`) instead of trusting raw headers unconditionally in `Request#shop`/`#topic`/`#webhook_id`. At minimum, document that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be used as a sole tenant-identity key without additional out-of-band verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and captures a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)` — the secret is the same for every installation of this app).
2. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - body = `B` (unchanged)
   - header `x-shopify-hmac-sha256: H` (unchanged)
   - header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - header `x-shopify-topic`, `x-shopify-webhook-id` (optionally changed)
3. `ShopifyAPI::Webhooks::Request.new` parses these headers into `shop`/`topic`/`webhook_id` [6](#0-5) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` — validation passes [7](#0-6) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, i.e., the host application processes attacker-controlled body content under the victim shop's identity [8](#0-7) .

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
