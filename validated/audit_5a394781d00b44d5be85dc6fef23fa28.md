### Title
Webhook HMAC Signature Does Not Bind the `shop`/`topic`/`webhook-id` Headers, Enabling Cross-Tenant Webhook Replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook processing pipeline verifies the HMAC signature over the raw request body only, while trusting the `shop`, `topic`, `webhook-id`, and `api-version` values from unauthenticated HTTP headers. An attacker who legitimately receives one genuine webhook (e.g. by installing the app on a shop they control) can capture the `(body, hmac)` pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and other) headers rewritten to identify a different, victim shop. Because the HMAC never covers these headers, the signature still validates, and the app's webhook handler executes with attacker-chosen shop/topic values as if the message genuinely originated from the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` purely from HTTP headers: [1](#0-0) 

But `to_signable_string`, which is what gets HMAC-verified, returns only the raw body: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the signature strictly from `verifiable_query.to_signable_string` (the body) and the app's `api_secret_key`, then does a constant-time comparison to the value from the `hmac-sha256` header — no header/shop/topic data participates in the signed material: [3](#0-2) 

`Webhooks::Registry.process` only calls this body-only HMAC check, then immediately trusts `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop that the verified bytes were produced for == shop the handler is told the event is about`. Because the HMAC covers only `@raw_body` and not the `shop-domain` header, this equality is not enforced — the verified bytes (body) can be paired with an arbitrary, unverified `shop` value.

### Impact Explanation
Any unprivileged internet user can create a development/trial shop and install the target app on it, thereby receiving genuine webhooks (valid `body` + valid `hmac-sha256`) signed with the app's shared `client_secret`/`api_secret_key`. Since the HMAC signature is independent of the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers, the attacker can resend that exact `(body, hmac)` pair while substituting the `x-shopify-shop-domain` header for any other shop that has the same app installed (shop identifiers/domains for public/multi-tenant apps are typically enumerable or knowable). `Webhooks::Registry.process` will accept the forged headers as valid because the HMAC check still passes, and will invoke the app's registered handler with `WebhookMetadata` claiming the event belongs to the victim shop. Depending on what the host app's handler does (e.g., updating shop-scoped state, uninstall/GDPR-type handlers, order/customer data ingestion keyed by `shop`), this allows cross-tenant data injection or corruption attributed to a shop the attacker does not control — a cross-tenant boundary violation.

### Likelihood Explanation
Likelihood is realistic: obtaining one valid `(body, hmac)` pair requires nothing more than installing the app on a shop the attacker controls (free/trial shops are trivially available), and replaying an HTTP POST with modified headers to the app's public webhook endpoint requires no special access, credentials, or privileged account. The only constraint is that the victim shop must also have the app installed, which is inherent to the app's normal user base.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie the trusted headers to the verified payload before use:
- Prefer verifying against Shopify's documented behavior where the `shop-domain` (and, ideally, `topic`/`webhook-id`) are corroborated independently (e.g., via a separate signed channel, or by requiring the receiving app to look up/validate that the shop is an installed, known tenant before trusting header-derived shop values for any state-mutating operation).
- At minimum, document/enforce that host applications must not use the unauthenticated `shop`/`topic`/`webhook_id` header values from `Webhooks::Request` for any privileged or cross-tenant-sensitive operation without additional verification, since the HMAC in `HmacValidator` only authenticates the raw body.
- Consider extending `Request#to_signable_string` (or the validator) to incorporate the header values that downstream code relies on, so a body/HMAC pair cannot be replayed against a different shop, topic, or webhook id.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they fully control) and triggers any webhook event; Shopify sends the app a genuine POST with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker captures `B` and the HMAC value.
3. Attacker sends their own POST to the app's webhook endpoint with the same body `B` and same HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers successfully: [5](#0-4) 
5. `Utils::HmacValidator.validate` returns `true` because it only checks `B` against the HMAC, which still matches: [6](#0-5) 
6. `Webhooks::Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` even though the payload was never produced by or for that shop: [4](#0-3)

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
