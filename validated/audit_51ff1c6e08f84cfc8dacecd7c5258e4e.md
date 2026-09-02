## Title
Webhook `shop-domain` Header Trusted Without HMAC Coverage, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity solely by checking the HMAC of the raw request body [1](#0-0) . However, the `shop` value that the handler receives and acts on is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never included in the HMAC-signed payload [2](#0-1) [3](#0-2) . This breaks the intended binding `hmac(body) == hmac(body, shop)`: the signature only proves the body's integrity, not which shop it belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `HmacValidator.validate` computes/compares the HMAC exclusively over that signable string [4](#0-3) . The `shop`, `topic`, and `webhook_id` fields are parsed straight from headers with no cryptographic binding to the signature [5](#0-4) .

`Registry.process` uses `Utils::HmacValidator.validate(request)` to confirm authenticity, then immediately trusts `request.shop` to build `WebhookMetadata` passed to the app's handler [6](#0-5) . Because the shop header is not covered by the signature, two different requests with the same body/HMAC pair but different `shop-domain` headers will both pass `HmacValidator.validate` — the equality the code implicitly relies on, `hmac_valid(body) == request_is_for(shop)`, does not hold.

### Impact Explanation
An attacker who legitimately controls a shop that has this app installed receives genuine webhooks with a valid HMAC (computed with the app's real secret, since Shopify signs it). Because the signature only covers the body, the attacker can capture one such legitimate webhook and resend it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop's domain, while the HMAC remains valid (the body is unchanged). `Registry.process` will accept it and invoke the handler with `shop: <victim-shop>` and the attacker-controlled body [7](#0-6) . Downstream app logic that keys off `data.shop` to select which tenant's data/session to mutate (a common pattern, as documented in `docs/usage/webhooks.md`) would then act on the victim shop using attacker-supplied data — a cross-tenant data-integrity break.

### Likelihood Explanation
Requires only an unprivileged attacker who is themselves a merchant/app installer (no theft of `api_secret_key`, no privileged account, no TLS interception needed) — the attacker uses their own genuinely signed webhook and simply retargets the `shop-domain` header before replaying it to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and topic/webhook id) in the HMAC-signable string, or otherwise cryptographically bind the shop domain to the signed payload before trusting `request.shop` in `Registry.process`. At minimum, the gem should document/enforce that `shop` must be cross-checked against a known list of active installed shops rather than trusted purely on the basis of body-HMAC validity.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook (e.g. `orders/create`) with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker resends the same body `B` and same HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) [8](#0-7) .
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B)` against the header, ignoring `shop` [9](#0-8) .
5. `Registry.process` calls the app's handler with `shop: "victim.myshopify.com"` and body `B`, even though this data never originated from Shopify for the victim shop [7](#0-6) .

### Citations

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
