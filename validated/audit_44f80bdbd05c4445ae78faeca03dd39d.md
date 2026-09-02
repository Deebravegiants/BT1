### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `ShopifyAPI::Webhooks::Registry.process` uses `Utils::HmacValidator.validate(request)` to authenticate the whole webhook and then trusts `request.shop` (read straight from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` header) to identify which tenant the webhook belongs to [2](#0-1) [3](#0-2) . The HMAC only binds the body bytes, not the shop identity, breaking the equality "bytes verified == bytes acted on."

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, which for a webhook `Request` is simply `@raw_body` [4](#0-3) [1](#0-0) . The `shop` field, however, comes from the `shopify-shop-domain` HTTP header, which is never included in the signed string [3](#0-2) .

`Registry.process` validates the HMAC and then immediately hands `request.shop` to the app's handler as the authoritative tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [2](#0-1) . Because the `client_secret`/`api_secret_key` used to sign webhooks is per-app, not per-shop, any merchant who installs the app receives genuine, validly-signed webhooks for their own store. Since the signature covers only the body, an unprivileged installer can replay that same body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header. `HmacValidator.validate` will still return `true` because the body bytes are unchanged, but `Registry.process` will construct `WebhookMetadata` pointing at the attacker-chosen victim shop rather than the shop that actually generated the request. This is exactly the identity-binding break the rules call out: a field ("shop") acted upon by the handler is not covered by the HMAC.

Any app that uses the `shop` value from `WebhookMetadata` to look up/act on a specific tenant's stored session or data (the intended and documented usage pattern) can be tricked into performing shop/tenant-scoped operations against the wrong shop, i.e. cross-tenant confusion originating purely from this gem's webhook verification logic.

### Impact Explanation
This falls under "Critical - cross-tenant access": an attacker controlling only their own (legitimately installed) shop can force the gem to report an attacker-chosen `shop-domain` for a validly-HMAC'd webhook payload, causing host applications that trust `WebhookMetadata#shop` (as documented/intended) to process events tagged for the wrong tenant.

### Likelihood Explanation
Likelihood is high for any unprivileged actor: no `api_secret_key`, access token, or credential leak is required. The attacker only needs to be a legitimate installer of the app on any shop (a standard, unprivileged interaction) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint, since the shop header is entirely attacker-controlled at the HTTP layer and outside of the HMAC's scope.

### Recommendation
Bind the shop identity into the HMAC-verified material, or independently corroborate `shop-domain` against a value obtained through an authenticated channel (e.g., verify it matches the shop referenced by the topic/webhook_id via a signed webhook payload field, or require the host app to cross-check `shop` against its own session/tenant records before trusting it). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be used as a sole tenant-identification source, or extend `Request#to_signable_string` semantics used by the gem to make clear the header is untrusted so integrators don't rely on it as verified.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a chosen body; Shopify signs it with the app's shared `client_secret`, producing headers `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures the raw body and the valid HMAC value.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the identical raw body and HMAC header, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only and matches, returning `true` [6](#0-5) .
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, so the app processes/acts on data as though it originated from `victim-shop.myshopify.com`, despite that shop having no involvement in the request.

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
