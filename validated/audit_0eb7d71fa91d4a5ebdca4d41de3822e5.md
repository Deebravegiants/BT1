### Title
Webhook `shop` domain is trusted for tenant routing but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the `shop` (and `topic`/`api-version`/`webhook-id`) values come from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the authoritative tenant identifier, without that value ever being covered by the signature that "proves" the message is genuine.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop` is read from a separate, unsigned header: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` uses this validation result as the sole authenticity gate, then forwards `request.shop` (never checked by the HMAC) to the handler as the trusted tenant identity: [4](#0-3) 

This is the exact class of defect described in the external report: a field that is *acted on* (here, `shop`, used by the app to attribute/store data per-merchant) is not part of the bytes that are cryptographically bound together (`feeGrowthOutside`/tick-boundary values in the analog; `shop-domain` here). Compare with `Auth::Oauth::AuthQuery`, where `shop` *is* included in `to_signable_string` and therefore is bound to the signature: [5](#0-4) 

Because the webhook HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is identical for every shop that installs the app, any HTTP endpoint holder who controls a legitimate installation on their own store can obtain a genuinely-signed webhook body/HMAC pair from Shopify for their own shop, then replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shopify-shop-domain` header. `HmacValidator.validate` still succeeds (it never looks at the shop header), so `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, alongside attacker-controlled body content.

### Impact Explanation
This breaks the identity binding: `equality(shop authenticated) == equality(shop stored/acted upon)` fails — the shop value the app trusts to route/store per-tenant data is never covered by the signature that is supposed to authenticate the message. Any app that keys per-shop side effects (order records, GDPR redaction requests, inventory updates, notifications, etc.) off `WebhookMetadata#shop`/`request.shop` can be made to apply attacker-supplied data to a victim shop's tenant space, i.e. cross-tenant data injection, using only an HMAC obtained from the attacker's own store — no access to the victim's or the app's secrets is required. This matches the Critical impact category "cross-tenant access."

### Likelihood Explanation
Any developer or org that can install the app on a shop they control (a very low bar — even a free/dev shop) can generate a validly-signed webhook body for their own shop and then forward it to the app's public webhook endpoint with a forged `shopify-shop-domain` (or `x-shopify-shop-domain`) header. No secret material beyond what Shopify legitimately gives that attacker (their own webhook payload) is needed, making this practically reachable by any unprivileged internet user who can install the target app once.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the HMAC-covered payload, or independently authenticate the shop domain against the set of shops actually installed/authorized for the app before using it as a tenant key — mirroring how `AuthQuery#to_signable_string` binds `shop` into its signature. At minimum, document/enforce that `WebhookMetadata#shop` must never be trusted without cross-checking it against a known/installed shop record before use.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, triggers a webhook (e.g. `orders/create`), and captures the raw POST: `raw_body` plus the `x-shopify-hmac-sha256` header. This HMAC is valid because it's signed by Shopify using the app's `client_secret` over `raw_body` only, per [6](#0-5) .
2. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body without complaint (`shop` header presence is only checked, not its consistency with the signature) — [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only verifies `raw_body` against the HMAC — [8](#0-7) .
5. The app's handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker-controlled parsed body>, ...)` and processes it as authentic data for the victim shop — [9](#0-8) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
