### Title
Webhook `shop` and `topic` attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively against that raw body [1](#0-0) . The `shop` (`shopify-shop-domain`), `topic`, `webhook-id` and `api-version` values, however, are read straight from HTTP headers and are never included in the signed payload [2](#0-1) . `Registry.process` validates the HMAC and then unconditionally trusts these unauthenticated header values to build the `WebhookMetadata` passed to the app's handler, which app code uses as the tenant identifier [3](#0-2) .

### Finding Description
The intended identity binding is: `shop attributed to the delivered webhook == shop that the HMAC-signed payload actually originated from`. Because the signature only covers `@raw_body`, that binding does not hold — the `shop-domain` header can be swapped for a different value while the same HMAC over the same body remains valid.

Since `api_secret_key` (the app's `client_secret`) is a single value shared across every shop that has installed the app (it is not per-shop), any shop that installs the app can generate a legitimate `(body, hmac)` pair for itself (by triggering a real webhook event on its own store), then replay that exact body+HMAC combination while substituting the `x-shopify-shop-domain` header for a different, victim shop's domain. `Request.new` performs no cross-check between the header value and the signed content: it only requires the required headers to be *present*, not that `shop` is bound to the signature [4](#0-3) . `Utils::HmacValidator.validate` will still return `true` because it only recomputes the HMAC over the untouched raw body [5](#0-4) .

`Registry.process` then dispatches the handler with `shop: request.shop` taken from that spoofed header, alongside `topic` and `body`, both of which can also be independently varied since only `raw_body` is signed and `topic`/`webhook-id` are read from separate, unsigned headers [3](#0-2) . Any host application that persists webhook data keyed by `WebhookMetadata#shop` (the documented, expected usage) will attribute attacker-controlled data to a different tenant.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce for webhook processing: `Registry.process` is presented as validating that a webhook is authentically from the shop it claims to be from ("Invalid webhook HMAC" check) [6](#0-5) , but the check never actually binds the shop identity to the signed content. This is a cross-tenant access vector: a shop that has installed the app can cause the app to process/store attacker-chosen payloads under a different shop's identity.

### Likelihood Explanation
Exploitation only requires the attacker to install the vulnerable app on their own (or a trial) store — no leaked secret, no privileged access, and no interaction with the app's `client_secret` value is needed. The attacker legitimately obtains a valid `(body, hmac)` pair for their own store and merely edits the outbound HTTP header before POSTing to the app's webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) header values in the HMAC-signed content check, or otherwise cryptographically bind the header-derived shop domain to the request before it is trusted, e.g. by validating the `shop` against a per-shop expected value tracked independently of the header, or requiring the app to confirm `WebhookMetadata#shop` corresponds to a shop with an active, matching installation before acting on the payload.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a real event (e.g. updates a product) so Shopify sends a legitimate webhook: raw body `B` with header `x-shopify-hmac-sha256: H` computed over `B` using the app's `client_secret`, and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical `B`/`H` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, which still matches `H`, so validation passes [7](#0-6) .
5. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, causing the host app to process/store the payload as if it came from the victim shop [8](#0-7) .

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
