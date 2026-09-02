### Title
Webhook shop identity (`shop-domain` header) is not covered by HMAC verification, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The gem's webhook HMAC verification only authenticates the raw request body. The `shop` value that the library hands to the app's `WebhookHandler` is read from an unauthenticated header and is never bound to the HMAC signature, breaking the equality `shop verified-by-HMAC == shop acted-on-by-handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC solely against that signable string [2](#0-1) . Meanwhile, `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, a value that plays no part in the HMAC computation [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to construct the `WebhookMetadata` that is dispatched to the app's handler, which uses `shop` to route/attribute the payload to a tenant: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) . `WebhookMetadata#shop` is a plain `String` field with no further verification [5](#0-4) .

Because a single `Context.api_secret_key` is shared across every shop installed on a multi-tenant app [6](#0-5) , any legitimate installer (an unprivileged internet user who has installed the app on their own shop and therefore can generate genuine webhook deliveries with a valid HMAC for arbitrary bodies they control, e.g. via triggering their own `orders/create` or similar) can capture one valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds, because the header is not part of `to_signable_string`, and `Registry.process` forwards the forged `shop` value to the handler unchanged.

### Impact Explanation
This is a cross-tenant identity confusion: the shop value that survives cryptographic verification (none — it's unauthenticated) is not the same as the shop value the host app's handler acts upon. An app that uses `WebhookMetadata#shop` (as the gem's own documented pattern intends) to look up per-shop session/API credentials, write to per-tenant data stores, or take shop-scoped actions can be made to attribute an attacker-controlled payload to a different, victim tenant — a cross-tenant access condition.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be able to install the app on any shop (self-service in the Shopify App Store model) to obtain one genuine `(body, hmac)` pair under the shared `api_secret_key`, and (2) send an HTTP POST to the app's public webhook endpoint with the same body/HMAC but a different `shop-domain` header — both are unprivileged, internet-reachable actions with no access token or leaked secret required.

### Recommendation
Bind the shop (and other routing-relevant headers such as topic/api-version) into the value verified by HMAC, or otherwise cryptographically tie the claimed shop to the verified body (e.g., include headers in the signable string via a canonicalized representation, or require the caller to separately validate `shop` against a known-installed-shops list before trusting it for tenant-scoped operations). At minimum, `Utils::HmacValidator` should authenticate the header set that downstream code treats as trusted identity, not only the JSON body.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (normal, unprivileged install flow) and triggers a webhook (e.g. `orders/create`) to their own endpoint, capturing the exact `raw_body` and the corresponding `x-shopify-hmac-sha256` value Shopify sent — both are valid for the app's single, shared `api_secret_key`.
2. Attacker crafts a new HTTP request to the app's webhook endpoint using the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully (headers only checked for presence, not shop authenticity) [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [8](#0-7) .
5. The handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` even though the payload/HMAC were never issued by or for that shop, and the app processes/attributes the data as belonging to the victim tenant.

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
