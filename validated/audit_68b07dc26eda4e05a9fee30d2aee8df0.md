This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates only that the body's HMAC matches, then forwards `request.shop` (the unauthenticated header) straight to the app's handler as the tenant identifier [3](#0-2) .

### Title
Webhook tenant identity (`shop`) is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw body bytes, but the `shop` (tenant identity) value that is handed to the app's handler is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is not included in the HMAC signature input at all.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac` [4](#0-3) . For webhook requests, `to_signable_string` returns only `@raw_body`; none of the HTTP headers — including the shop-domain header — are part of the signed material [1](#0-0) .

`Registry.process` uses this same `HmacValidator.validate(request)` call as its sole authentication check, and then immediately trusts `request.shop` — sourced purely from the header via `shopify_header("shop-domain")` — to build the `WebhookMetadata` passed to the app's handler [5](#0-4) [2](#0-1) .

This is the identity-binding break the analog rules call out: "a field acted on but not covered by the HMAC." The equality that should hold is `shop (used to route/attribute the webhook) == shop (bound by the signature)`, but here the gem only enforces `hmac(raw_body) == received_hmac`, with `shop` entirely outside that binding. Because the `shopify-hmac-sha256` value only signs the body, an attacker who can capture or replay any single valid `(raw_body, hmac)` pair signed by the shared `client_secret` — e.g., their own shop's own legitimate webhook delivery, or one they can trigger for a shop under their control — can replay it to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a different, victim shop. `Registry.process`'s HMAC check still passes, since it never looks at the header, and the handler receives `WebhookMetadata` claiming the body originated from the victim shop [6](#0-5) .

### Impact Explanation
This qualifies as cross-tenant access (Critical): a host application that uses `request.shop`/`data.shop` from `ShopifyAPI::Webhooks::Registry.process` to key its per-tenant records (as the documentation explicitly instructs apps to do — see the sample handler forwarding `data.shop` as `shop_domain` [7](#0-6) ) can be tricked into attributing attacker-controlled webhook content to an arbitrary victim shop, corrupting or exfiltrating data across tenant boundaries, since the shop attribution itself is unauthenticated.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one validly-signed `(raw_body, hmac)` pair — trivially obtainable by creating their own development/trial shop, installing the app, and capturing a webhook Shopify sends them (since HMAC uses the app's shared secret, not a per-shop key). They then only need to change one HTTP header value when replaying the request to the app's public webhook endpoint. No access token, secret, or privileged account is required.

### Recommendation
Include the shop domain (and ideally the webhook id / topic, to prevent header-substitution replay across topics) inside the HMAC-signed material, or otherwise verify the received `shop-domain` header against the shop derivable from other authenticated data before trusting it for tenant attribution. At minimum, document that host apps must not rely on `shop`/`data.shop` from `Registry.process` for tenant identification without independent verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) to receive a validly signed `(raw_body, x-shopify-hmac-sha256)` pair from Shopify, signed with the app's `client_secret`.
2. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only presence, not shop-hmac binding, is checked) [8](#0-7) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [9](#0-8) .
5. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload came from the attacker's own shop, and the host app processes it as victim-shop data.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
