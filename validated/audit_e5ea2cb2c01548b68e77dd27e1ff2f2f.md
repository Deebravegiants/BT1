### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` value that is subsequently trusted and handed to the host application's handler comes from an HTTP header that is never included in the signed content. This breaks the intended binding of "the shop whose secret produced this signature" == "the shop this webhook is attributed to," letting an attacker replay a genuinely-signed payload while swapping in an arbitrary target shop domain.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the bytes that get signed as only the raw body: [1](#0-0) 

The `shop` accessor, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which plays no part in `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the request by recomputing the HMAC exclusively over `to_signable_string` (the body) and comparing it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this same validation and, once it passes, forwards `request.shop` straight into `WebhookMetadata` without any additional check that the shop is the one the signature actually belongs to: [4](#0-3) [5](#0-4) 

The identity binding the library implicitly claims to provide is:
`shop that produced a valid HMAC (via the app's shared client_secret) == shop attributed to and processed for this webhook (request.shop passed to the handler)`

Because the header is excluded from the signed bytes, this equality does not hold. The `client_secret`/HMAC key is shared across all shops that install a given app (it is not shop-specific), so any merchant that has installed the app and can observe genuine webhooks sent to their own shop possesses a `(body, hmac)` pair that is valid under the app's secret. That same attacker can send this untouched, validly-signed body to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion in a security-critical binding the library is trusted to provide: host applications rely on `WebhookMetadata#shop` (as returned by this library, having already "verified" the webhook) to decide which tenant's data/session to act on. An attacker-controlled shop can cause the library to authenticate a webhook body as if it came from a different (victim) shop, letting the attacker inject spoofed events attributed to another merchant's store — a cross-tenant access outcome.

### Likelihood Explanation
Any account that can install the target app (a normal, unprivileged merchant) automatically receives legitimately-signed webhooks for their own shop and can trivially intercept and replay them with a modified header value against the app's public webhook endpoint. No access to the `client_secret`, access tokens, or any other shop's credentials is required — only observation of one's own valid webhook traffic and the ability to send an HTTP request with custom headers.

### Recommendation
Include the shop domain (and ideally topic/api-version) as part of the signed/verified material, or otherwise cryptographically bind the `shop` value to the HMAC-covered payload before it is trusted. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should not allow `Registry.process` to treat any header-derived field as authenticated when it is excluded from `to_signable_string`. If Shopify's real webhook HMAC scheme genuinely only ever covers the body (as documented upstream), the library should not present `request.shop`/`WebhookMetadata#shop` as verified/trusted; documentation and API should make explicit that consumers must independently confirm the shop is one they expect for this specific webhook subscription/registration before acting on it.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify sends the app a legitimate webhook: `raw_body = '{"id":1,...}'` with header `X-Shopify-Hmac-Sha256: <valid hmac over raw_body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact `(raw_body, hmac)` pair.
4. Attacker POSTs the same `raw_body` and `hmac` header to the app's webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) — [6](#0-5) .
6. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` and succeeds, since the body/hmac pair is unmodified — [7](#0-6) .
7. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, letting the attacker inject or spoof events attributed to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
