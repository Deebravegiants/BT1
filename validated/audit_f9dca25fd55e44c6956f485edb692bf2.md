### Title
Webhook shop-domain header is not covered by the HMAC, allowing tenant confusion on replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then passes an unauthenticated `shop` value taken from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header straight to the consuming application's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the HMAC exclusively against that signable string [2](#0-1) . Meanwhile `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signed bytes [3](#0-2) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., validates the body) and then immediately forwards `request.shop` into `WebhookMetadata` for the handler to consume as the tenant identifier [4](#0-3) . No call to `ShopValidator` or any other mechanism binds the header-derived shop to the HMAC-covered payload.

This breaks the identity binding: `HMAC-verified bytes == raw_body` but `shop identity used by handler == header value`, i.e. `bytes_verified ≠ bytes_that_determine_tenant`. Anyone who has ever received one legitimate webhook delivery from Shopify (e.g., by installing the app on their own store, an "unprivileged" action) possesses a `(raw_body, valid_hmac)` pair. Because the shop header is excluded from the signed content, that captured pair can be replayed to the same webhook endpoint with the `shopify-shop-domain` header rewritten to an arbitrary victim shop domain, and the HMAC check in `Registry.process` will still pass [5](#0-4) .

### Impact Explanation
This qualifies as cross-tenant access: an app's webhook handler typically uses `data.shop` to look up the merchant's stored session/access token and to determine which tenant's data to mutate (e.g., process an order, revoke access, redact data). By replaying a captured, validly-signed webhook body while spoofing the `shop` header, an attacker (who only needs to have installed the app once on their own store) can cause the host application to attribute the webhook's body/action to a different shop than the one that actually produced it, without ever needing the app's `client_secret` or another shop's access token.

### Likelihood Explanation
Exploitability depends on the attacker being able to capture at least one legitimate webhook (body + HMAC) — trivially achievable by installing the app themselves, since Shopify sends real webhooks (e.g. `app/uninstalled`, `orders/create` if scopes allow) to any installed shop's configured endpoint. Rewriting the `shop`-domain header on a replayed HTTP request requires no cryptographic secret. The main mitigating factor is that many host applications may perform their own additional shop verification outside this gem, but the gem itself provides no such guarantee and its own webhook-processing API (`Registry.process`) hands over an unauthenticated `shop` value as if it were verified.

### Recommendation
Bind the shop identity to the HMAC-verified content, e.g., include the `X-Shopify-Shop-Domain` header value (and ideally `topic`/`webhook-id`) in the bytes that are HMAC-verified (similar to how Shopify's newer webhook formats or other verification schemes bind headers), or explicitly document/enforce that consumers must independently verify `data.shop` belongs to a shop with an active, known installation/session before trusting it, and validate it through `ShopifyAPI::Utils::ShopValidator` at minimum to ensure it's a well-formed Shopify domain rather than an arbitrary value.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled store `attacker.myshopify.com`; capture a genuine webhook delivery, e.g.
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Webhook-Id: ...
   Body: {"id":123, ...}
   ```
2. Replay the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but change the header:
   ```
   X-Shopify-Shop-Domain: victim.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (unchanged) body against the (unchanged) HMAC [5](#0-4) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` [7](#0-6)  even though the payload actually originated from the attacker's own shop, demonstrating the tenant-binding break.

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
