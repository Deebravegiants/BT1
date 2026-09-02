This confirms the vulnerability: the webhook `shop` identifier is sourced entirely from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [1](#0-0) , while the HMAC that `Registry.process` validates only covers the raw request body bytes [2](#0-1) [3](#0-2) . The `shop` value is never included in `to_signable_string`, so it is not bound to the signature at all.

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) purely from the `X-Shopify-Shop-Domain` header, but `Utils::HmacValidator.validate` only verifies the HMAC over `@raw_body` returned by `to_signable_string`. The shop header is completely outside the cryptographically verified payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [2](#0-1) , and `Request#shop` reads directly from the incoming header without any cross-check against the signed content [1](#0-0) . `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the header-provided HMAC [4](#0-3) . `Registry.process` calls this validator and, if it passes, immediately trusts `request.shop` to build `WebhookMetadata` that is handed to the app's `WebhookHandler` [3](#0-2) .

The identity binding that should hold is: `shop header == shop bound inside HMAC-covered bytes`. In this implementation that equation is never enforced — the HMAC only proves the body bytes were signed by Shopify with the app's `client_secret`; it says nothing about which shop the header claims to be.

Because the same `client_secret` (and therefore the same HMAC secret) is shared across every shop that installs the app, a merchant who installs the app on their own store ("Shop A") receives genuine webhook deliveries with a valid `X-Shopify-Hmac-Sha256` value computed over their own body. That merchant, as an ordinary unprivileged actor with respect to any other tenant of the same app, can capture one such raw body + HMAC pair and replay it to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value (e.g., a competitor's shop domain, or their own shop's domain reused to replay stale data into another topic/handler context). `HmacValidator.validate` still returns `true`, since it only checks body-signature integrity, and `Registry.process` will hand the forged `shop` value straight to the app's handler.

### Impact Explanation
This breaks tenant isolation: the app's webhook handler receives a `shop` value that is not bound to, or verifiable against, the cryptographic proof of authenticity. Any host application that uses `WebhookMetadata#shop` (as documented/intended, e.g., to look up per-tenant credentials, write per-tenant data, or trigger tenant-scoped side effects) can be tricked into attributing another tenant's data/events to the attacker-chosen shop, or vice versa — a cross-tenant confusion primitive reachable by any merchant who has legitimately installed the app once.

### Likelihood Explanation
Any merchant who installs the app (a normal, unprivileged flow) automatically receives valid signed webhook bodies from Shopify for their own store, satisfying the "no privileged credentials required" constraint. Replaying that body to the public webhook endpoint with a modified shop header is a simple HTTP request; no access token, `client_secret`, or TLS interception is needed.

### Recommendation
Bind the shop identity into the value that is actually verified. Include the `shop-domain` header (and ideally `topic`/`webhook-id`) inside `to_signable_string`'s equality check, or independently validate that `request.shop` matches a shop already known to be associated with the webhook subscription/session before trusting it in `WebhookMetadata`. At minimum, document and enforce that host applications must not use the unauthenticated `shop` field for tenant-scoped decisions without additional verification (e.g., cross-checking against a known list of shops that have installed the app).

### Proof of Concept
1. Merchant installs the app on `attacker-shop.myshopify.com` and captures a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`).
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Request.new` accepts the headers/body [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [6](#0-5) .
4. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop == "victim-shop.myshopify.com"` and passed to the app's handler, even though the payload `B` was never actually associated with that shop by Shopify [7](#0-6) .

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
