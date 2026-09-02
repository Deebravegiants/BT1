This confirms the finding. The `Webhooks::Request` class only binds `@raw_body` into the HMAC signature via `to_signable_string`, while `topic`, `shop`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers and passed downstream to the host application's handler as trusted identity fields.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing on replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that body [1](#0-0) [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` fields are parsed straight from HTTP headers that are never part of the signed payload [3](#0-2) , yet `Registry.process` trusts `request.shop` as the tenant identity when dispatching to the host application's handler [4](#0-3) .

### Finding Description
The binding that should hold is: `bytes verified by HMAC == bytes the identity (shop) is derived from`. In this gem that equality is broken: the HMAC is computed and checked only over `@raw_body` [5](#0-4) , while the `shop` attribute used downstream as the tenant identifier is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which sits completely outside the signature [6](#0-5) .

Because a genuine webhook the app receives for Shop A carries a body and HMAC that were both generated with the app's own `client_secret` by Shopify, an attacker who controls Shop A (an ordinary merchant who installed the app) can capture that valid `(raw_body, hmac)` pair from their own legitimate webhook deliveries and resend the exact same bytes to the app's webhook endpoint while substituting the `shop-domain` header for Shop B. `Utils::HmacValidator.validate` recomputes the HMAC over the identical body and secret and returns `true` [7](#0-6) , because the header change never touches `to_signable_string`. `Registry.process` then dispatches to the registered handler with `shop: request.shop` set to the spoofed Shop B value alongside Shop A's body content [8](#0-7) , so the handler processes attacker-controlled data while believing it originates from, and applies to, Shop B's tenant.

This is a direct analog of the reported bug class: a field ("shop") that is acted upon (used as the tenant/session key by the handler) is not covered by the authentication mechanism (HMAC), just as the report's `minOutAmount` calculation trusted an unverified 1:1 peg for a value it treated as authoritative.

### Impact Explanation
This crosses a tenant boundary: an unprivileged holder of one shop's installation can forge webhook events that the host application will attribute to a different, arbitrary shop, without ever needing that shop's credentials, access token, or `client_secret`. Depending on how the host app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to look up a session/access token for that shop, update per-shop records, or trigger `shop/redact`/`customers/redact` compliance flows), this enables cross-tenant data corruption or spoofed compliance actions against victim shops — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any app that installs the standard `ShopifyAPI::Webhooks::Registry.process` flow as documented: any merchant who installs the app can trivially capture legitimate `(body, hmac)` pairs delivered to their own endpoint and replay them with a modified `shop-domain` header from any HTTP client, requiring no secrets, no privileged access, and no protocol violations by the host app.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the HMAC-signed payload (or otherwise cryptographically bind them to the body), so `to_signable_string` in `lib/shopify_api/webhooks/request.rb` covers the full set of trusted fields, not just the raw body. Alternatively, require host applications to independently verify `request.shop` corresponds to a shop that actually has this webhook/topic subscription registered (with per-shop unique webhook ids) before trusting it in `Registry.process`.

### Proof of Concept
1. Attacker installs the app for `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over body B>`, and body `B`.
3. Attacker replays the exact same body `B` and HMAC header to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [9](#0-8) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the unmodified body `B` against the unmodified HMAC [10](#0-9) .
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's body B>, ...)` [8](#0-7) , causing the host app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
