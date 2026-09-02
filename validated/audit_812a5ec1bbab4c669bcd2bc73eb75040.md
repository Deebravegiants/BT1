This confirms the design: `Registry.process` is documented as verifying "the request did indeed come from Shopify," and the handler is told to trust `data.shop` as "The shop domain of the webhook" — but the HMAC only covers the raw body.

## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by calling `Utils::HmacValidator.validate(request)`, which asserts an equality between `computed_signature = HMAC(secret, request.to_signable_string)` and the received `hmac`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor, however, is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header and is never mixed into the signed bytes [2](#0-1) . `Registry.process` passes this unverified `shop` straight to the app's handler as the tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [3](#0-2) .

### Finding Description
The equality the gem is supposed to guarantee is: `bytes verified by HMAC == bytes the app trusts as belonging to a shop`. Here that equality is broken: `HmacValidator.validate` only proves `HMAC(secret, raw_body)` is correct [4](#0-3) ; it says nothing about which shop the body belongs to, because `shop` is a plain header value that is excluded from `to_signable_string`.

Since any app owner (including an attacker) can legitimately install the target app on their own shop and receive genuine Shopify webhooks — each with a correctly computed `hmac-sha256` header for that body — the attacker possesses valid `(raw_body, hmac)` pairs signed by Shopify with the app's real secret. Nothing stops the attacker from replaying that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Webhooks::Request.new` only requires that a `shop-domain` header be present, not that it match anything [5](#0-4) , and `HmacValidator.validate` will still return `true` because the body and HMAC are untouched. The application layer then processes the attacker-controlled payload believing it originates from the victim's shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: the field the app relies on to route webhook data to a specific merchant's tenant (`shop`) is not part of the cryptographically verified payload. An attacker can inject data purportedly belonging to another shop into any app logic keyed off `data.shop` (e.g., queued jobs, per-shop database writes/lookups, GDPR/compliance webhook handling), leading to cross-tenant data confusion/injection. This matches the "Critical - cross-tenant access" impact category since it lets an unprivileged user (any app installer) make the app act on behalf of a shop they don't control.

### Likelihood Explanation
Likelihood is high for any app: installing the target app on an attacker-owned development/trial shop is trivial and free, giving the attacker an unlimited supply of validly-signed `(body, hmac)` pairs to replay against the shared, public webhook endpoint with an arbitrary `shopify-shop-domain` header.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-covered signable string, or otherwise cryptographically tie the header value to the payload/secret so `Utils::HmacValidator` cannot pass when the shop has been substituted. Alternatively, `Registry.process`/`WebhookMetadata` should require the caller to independently verify that `request.shop` corresponds to a shop that actually has this specific `webhook_id`/subscription registered before trusting it as the tenant identifier.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com`, triggers a webhook (e.g. `orders/create`) and captures the raw POST body plus its `x-shopify-hmac-sha256` header — both validly signed by Shopify using the app's real `api_secret_key`.
2. Attacker POSTs the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unaffected by the shop header — and returns `true` [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, and the app processes/stores this data as though it came from the victim's tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
