This confirms the vulnerability path. The `Webhooks::Request#to_signable_string` returns only `@raw_body` (the request body), while `shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never part of the HMAC-signed material. `Registry.process` validates only the body's HMAC and then passes the header-derived `shop` straight into `WebhookMetadata` handed to the app's handler, so the shop identity a handler trusts is unauthenticated.

### Title
Webhook shop identity is not HMAC-bound, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with `to_signable_string` returning only the raw request body [1](#0-0) , while `shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` computes the HMAC over exactly `to_signable_string` (the body) using the app's `api_secret_key` and compares it to the `hmac` header [3](#0-2) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` and then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` straight to the app-supplied handler [4](#0-3) .

The broken identity equality is:
`shop_covered_by_hmac (none, body-only) != shop_trusted_by_handler (WebhookMetadata#shop, from unauthenticated header)`

Because Shopify's app `api_secret_key`/`client_secret` is a single app-wide secret shared across every shop that installs the app (not per-shop), any merchant who installs the app can legitimately receive webhooks with a valid HMAC over a body they fully control (e.g., by triggering an event on their own store, or simply crafting any JSON body and computing HMAC — for topics processed generically as JSON, `parsed_body` just calls `JSON.parse(@raw_body)` [5](#0-4) ). That attacker-controlled (body, hmac) pair remains valid for HMAC purposes regardless of which `shop-domain` header value accompanies it, since the header is excluded from the signable string.

### Impact Explanation
An attacker who installs the target app on their own store (a legitimate, unprivileged action available to any internet user who can install a public Shopify app) can compute a valid HMAC for an arbitrary JSON body using the app's shared secret via a real webhook delivery to themselves, then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. Because `Registry.process` only re-validates the HMAC of the body [6](#0-5) , this forged request passes verification and the handler executes believing `data.shop` is the victim shop. Any app logic that uses `WebhookMetadata#shop` to select the tenant record to update (order status, inventory, customer PII, mandatory GDPR webhooks such as `customers/redact`/`shop/redact`, etc.) is thereby exposed to cross-tenant data corruption or disclosure using only the attacker's own valid app installation — no access token, `client_secret`, or victim credentials are required.

### Likelihood Explanation
Any internet user can install a Shopify app they target (standard install flow) and thereby legitimately obtain valid `(body, hmac)` pairs signed with the app's shared secret. The `shop-domain` header is attacker-controlled HTTP input, so forging it and replaying the request requires only basic HTTP tooling. Nothing in `Utils::HmacValidator` or `Webhooks::Registry.process` prevents this because the shop field is architecturally excluded from the signed payload.

### Recommendation
Include the shop-domain header value in the material covered by the HMAC (e.g., concatenate it with the body before signing/verifying), or otherwise cryptographically bind the `shop` claim to the signed webhook payload before it is exposed via `WebhookMetadata#shop`. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated and must never be used by handlers to select a tenant without an independent, out-of-band verification (e.g., cross-checking against a `shop` value embedded in the signed body, or against the shop associated with the registered `webhook_id` via the Admin API).

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, obtaining legitimate webhook deliveries.
2. Attacker captures one such delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — valid per `HmacValidator.validate_signature` [3](#0-2) .
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses headers/body normally [7](#0-6) ; `Registry.process` calls `HmacValidator.validate(request)`, which passes because it only checks body `B` against `H` [6](#0-5) .
5. The registered handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [8](#0-7)  and performs tenant-scoped actions against the victim shop's data using attacker-supplied body content, despite the attacker never having any credentials for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L40-43)
```ruby
      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
