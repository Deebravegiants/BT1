### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while the `shop` value that is handed to the app's handler as the tenant identifier is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . The equality the gem is supposed to enforce is: `hmac_signed_bytes == bytes_that_determine_the_acted-upon_shop`. Instead, the signed bytes are `raw_body` only, and the acted-upon shop comes from a header that is never part of the signable string, so the binding is broken.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it (via `OpenSSL.secure_compare`) to the `hmac` provided by the request [3](#0-2) . For webhook requests, the "signable string" is defined as just the raw request body [1](#0-0) , matching Shopify's actual webhook HMAC scheme (HMAC-SHA256 over the body using the shared `client_secret`).

`Registry.process` uses this validation as the sole authentication gate, then immediately trusts `request.shop` (parsed from the `shop-domain` header, not from the signed body) to build `WebhookMetadata` and dispatch it to the app's handler as the shop the event belongs to [4](#0-3) .

Because the same `client_secret` is shared by the app across every merchant/shop that installs it, and the HMAC never covers the `shop-domain` header, any party that has received one legitimately-signed webhook body+HMAC pair for the app (e.g., a merchant who installed the app on their own store and can freely trigger webhook events, or anyone who can observe a raw webhook delivery) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different `shop-domain` header value. `HmacValidator.validate` will still return `true` (it only checks the body against the HMAC), and `Registry.process` will dispatch the event to the handler tagged with the attacker-chosen shop domain, even though the shop never produced or authorized that event [5](#0-4) .

This is analogous to the `CDPVault` bug: a value (`takeCollateral`) is acted upon (transferred) without applying the transformation (`tokenScale`) that the rest of the system consistently applies to keep internal and external representations consistent. Here, a value (`shop`) is acted upon (used as the tenant key for dispatching webhook data) without being covered by the transformation (HMAC binding) that the rest of the system relies on to guarantee authenticity.

### Impact Explanation
This allows cross-tenant confusion: an attacker can cause the app to process/attribute a webhook event under an arbitrary shop domain of their choosing, while the HMAC check passes. Depending on what the host application does with `WebhookMetadata#shop` (e.g., look up per-shop session/access tokens, trigger per-shop side effects, write audit data keyed by shop), this can lead to cross-tenant data confusion or spoofed events being attributed to a victim shop — a High-severity tenant-isolation break enabled entirely by this gem's request-parsing/validation design, not by host misuse.

### Likelihood Explanation
Exploitation requires the attacker to already possess one legitimately HMAC-signed webhook body for the target app (trivially obtainable by installing the app on their own shop and triggering any webhook topic, since the same `client_secret` signs all shops' webhooks for that app) and the ability to POST to the app's public webhook endpoint with a modified `shop-domain` header — both are unprivileged-internet-user actions once the attacker has installed the app once. No access token, refresh token, or `client_secret` leakage is required.

### Recommendation
Include the shop domain (and other identity-relevant headers such as topic and API version) in the bytes that are HMAC-verified, or otherwise cryptographically bind the header-derived `shop` value to the signed payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be corroborated against Shopify's known shop list by the host application, or change `Request#to_signable_string`/`HmacValidator` to also cover the shop-domain header value.

### Proof of Concept
1. App installs and receives one real webhook delivery for shop `attacker.myshopify.com`, topic `orders/create`, with headers `x-shopify-hmac-sha256: <H>` and `x-shopify-shop-domain: attacker.myshopify.com`, and body `B`.
2. Attacker replays the exact same body `B` and `hmac-sha256` header `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers_with_victim_shop)` builds successfully (headers presence check only) [6](#0-5) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation passes [7](#0-6) [8](#0-7) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)`, even though `victim.myshopify.com` never sent this event [9](#0-8) .

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
