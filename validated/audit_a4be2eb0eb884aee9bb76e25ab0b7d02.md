### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight to the handler as the tenant identifier, without that header ever being part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` bind the HMAC signature only to `@raw_body`: [1](#0-0) 

The `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from unauthenticated HTTP headers and are never mixed into `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then constructs `WebhookMetadata` using `request.shop` — the unauthenticated header value — as the tenant key passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` only re-computes the signature over `verifiable_query.to_signable_string` (the body) and compares it to the received signature — it has no visibility into, and therefore cannot bind, the `shop` header: [4](#0-3) 

This breaks the intended identity binding: **shop authenticated (i.e., cryptographically proven to have originated from Shopify for this app) ≠ shop stored/used as the tenant key** that the host application uses to look up sessions, scope data access, or route webhook side effects. The `api_secret_key` used to compute the HMAC is a single per-app secret shared across every merchant that installs the app — it is not shop-specific — so the HMAC only proves "this body was sent for *some* shop of this app," not "this body was sent for *this* shop."

### Impact Explanation
An attacker who controls (or has installed) any shop with the vulnerable app can capture a legitimately signed webhook payload/HMAC delivered to their own endpoint (raw body + `x-shopify-hmac-sha256`), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different value in `x-shopify-shop-domain` (or `shopify-shop-domain`) naming a victim shop. `Utils::HmacValidator.validate` still succeeds because it only checks the body signature, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. If the host application trusts `data.shop` from `WebhookMetadata` to select which merchant's session/record to update (the pattern this gem's own webhook API is built around), this results in cross-tenant data corruption/access — one tenant's webhook event applied to another tenant's data.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the app on any shop (or otherwise obtain one valid signed webhook body/HMAC pair for that app) and then send an HTTP POST to the app's public webhook endpoint with a forged shop-domain header — no access token, `api_secret_key`, or privileged account is needed. The gem does nothing to prevent this; it explicitly documents `data.shop` as the identifying field for webhook handlers, encouraging host apps to trust it directly.

### Recommendation
Include the shop domain (and preferably the topic and webhook id) inside the HMAC-covered signable content, or independently verify that the shop named in the header matches a shop that is expected to be sending this specific webhook (e.g., cross-check against an active, previously stored session/shop record) before dispatching to the handler. At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be trusted without additional verification against known installed shops.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g., `orders/create`) and capture the raw POST body `B` and its `x-shopify-hmac-sha256: H` header (both valid, since Shopify computed `H = HMAC-SHA256(api_secret_key, B)`).
2. Replay the request to the same app's webhook endpoint with headers:
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-shop-domain: victim.myshopify.com` (forged)
   - `x-shopify-topic: orders/create`
   - body `B` (unchanged)
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"`, even though the payload actually originated from the attacker's own shop, letting the attacker inject/replay events attributed to a victim tenant.

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
