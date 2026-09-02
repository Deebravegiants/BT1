## Title
Webhook HMAC only covers the request body, allowing the `shop`, `topic`, and `webhook-id` headers to be forged without invalidating the signature — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery#to_signable_string` by returning only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only checks that the body matches the HMAC computed with the app's `api_secret_key`; it never binds the header values to that signature. `Registry.process` then passes the header-derived `request.shop` straight into `WebhookMetadata`, which is delivered to the app's handler as the trusted tenant identifier. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
The gem's own `VerifiableQuery` abstraction is used in two places:

- `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` (and `code`, `host`, `state`, `timestamp`) inside the signed payload, so the shop identity is cryptographically bound to the HMAC: [4](#0-3) 

- `Webhooks::Request#to_signable_string`, by contrast, returns only `@raw_body` — the `shop`, `topic`, `api-version`, and `webhook-id` values (all sourced from `shopify_header`, i.e. plain HTTP headers) are excluded from the signed material: [5](#0-4) 

`HmacValidator.validate` verifies `hmac` against `to_signable_string` alone using `OpenSSL.secure_compare`, so it never notices header tampering: [6](#0-5) 

`Registry.process` then dispatches the handler using `request.shop` (the unauthenticated header) as the tenant identity, alongside the HMAC-validated `request.parsed_body`: [3](#0-2) 

This breaks the identity binding: `shop_that_signature_covers` (nothing — signature covers only body bytes) ≠ `shop_delivered_to_handler` (`request.shop`, taken from an attacker-controllable header). Anyone who can trigger a legitimate webhook for their own installed shop (any merchant, with no special privilege) can capture a genuine `(body, HMAC)` pair computed with the app's real `api_secret_key`, then replay that exact body and HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a different shop's domain. Since those headers are outside the signed content, `HmacValidator.validate` still returns `true`, and the handler receives `WebhookMetadata` claiming the forged shop as the source of the (attacker-controlled) payload.

### Impact Explanation
This is a cross-tenant identity-binding break at the library level: the shop identity is not covered by the HMAC that the gem asserts guarantees authenticity, yet the gem hands the header-derived `shop` value directly to the app's handler as the trusted, HMAC-verified source. Applications that rely on `WebhookMetadata#shop` (as documented/intended) to route or attribute the (verified) body to a tenant can be made to process attacker-supplied data under a victim shop's identity — a cross-tenant confusion that only requires the attacker to control their own shop/app installation, no privileged credentials needed.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to install the app on their own store (or otherwise trigger a webhook topic they control), capture the raw HTTP request Shopify sends to the app's public webhook endpoint, and replay it with a modified `shop-domain`/`topic` header — all doable with a simple HTTP proxy, no secrets or elevated access needed.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) as part of `to_signable_string` in `Webhooks::Request`, mirroring how `AuthQuery` binds `shop` into its signed content, so that tampering with any of these headers invalidates the HMAC. At minimum, `shop` must be bound to the signature before it is trusted as the tenant identifier passed to `WebhookMetadata`.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) with attacker-chosen JSON body `B`. Shopify computes `HMAC = HMAC-SHA256(api_secret_key, B)` and sends:
```
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <HMAC>
X-Shopify-Shop-Domain: attacker.myshopify.com
Body: B
```
2. Capture this request via a proxy on the attacker's own receiving endpoint/inspection.
3. Replay the identical body `B` and `X-Shopify-Hmac-Sha256` value to the same app's public webhook URL, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the signature over `B` only and matches — validation passes.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)` and invokes the app's handler, which believes this attacker-controlled body is a signed, authentic event from `victim.myshopify.com`. [1](#0-0) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
