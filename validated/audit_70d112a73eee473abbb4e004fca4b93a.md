Confirmed. I have enough to finalize the analog analysis.

### Title
Webhook `shop-domain` identity is not covered by the HMAC signature, allowing cross-tenant event spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body via `Utils::HmacValidator.validate`, whose signable string is defined by `Request#to_signable_string` as `@raw_body` only [1](#0-0) . The `shop` value that is later handed to the host application's handler is read directly and unauthenticatedly from the `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) , which is never part of the HMAC-covered bytes.

### Finding Description
`Registry.process` performs exactly one authentication check — the HMAC over the body — then immediately dispatches to the handler using `request.shop`, `request.topic`, etc. taken from headers: [3](#0-2) 

The binding the library is implicitly promising is: `hmac_valid(raw_body) ⇒ (raw_body, shop) authentically originated together from Shopify for that shop`. In reality the equality that holds is only `hmac_valid(raw_body)`; the `shop` header is disjoint from the signed material, so:

`verified(raw_body) ⊅ verified(shop)`

Because the header value is attacker-controllable while the signature covers only the body, any party capable of sending a request whose body/HMAC pair is valid for the app's secret (e.g., an actual merchant who has installed the app and can capture/replay their own genuinely-signed webhook deliveries, since Shopify webhook bodies do not embed the destination shop domain) can resend that same `raw_body` + `hmac` pair with an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` only re-derives the signature from `to_signable_string` (the body) and compares it via `OpenSSL.secure_compare`, never inspecting or binding the shop header [4](#0-3) . `WebhookMetadata` then carries this unauthenticated `shop` straight into `handler.handle` [5](#0-4) , so any tenant-scoping logic in the host app that trusts `data.shop` is misled.

### Impact Explanation
This crosses a tenant boundary: a webhook that is cryptographically valid can be attributed to any shop of the attacker's choosing, letting a merchant who owns one shop cause the host application to apply the payload (order data, customer data, product data, etc.) as if it belonged to a different shop. This matches the "Critical – cross-tenant access" impact category since it lets one tenant's authenticated data stream be relabeled as another tenant's data within the host app.

### Likelihood Explanation
Moderate-to-high: the attacker needs no secret material — only the ability to install the app on a shop they control (which is the normal, unprivileged path for any Shopify merchant/developer) to obtain a genuinely HMAC-signed webhook body, and then to replay it with a modified `shop-domain` header directly against the app's webhook endpoint. No TLS interception, leaked credentials, or privileged access is required; the gem's own `Request`/`Registry` code performs no header-to-signature binding.

### Recommendation
Bind the shop identity to the signed payload before trusting it: either include the shop domain in the signable string used for HMAC validation, or independently corroborate the header-provided shop against a value that is cryptographically tied to the specific webhook subscription/session (e.g., cross-check against the registered `webhook_id`/topic-to-shop mapping known to the app, or require verification of the value through a Shopify API call) before constructing `WebhookMetadata`. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Merchant M installs the app on `m.myshopify.com`; Shopify delivers a webhook to the app's endpoint with body `B` and header `shopify-hmac-sha256: HMAC(secret, B)`, `shopify-shop-domain: m.myshopify.com`.
2. M captures this request and resends it to the same endpoint, keeping `B` and the HMAC header identical but changing the header to `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`B`) — unchanged — and passes [7](#0-6) .
5. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` and processes M's data as belonging to `victim.myshopify.com`.

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
