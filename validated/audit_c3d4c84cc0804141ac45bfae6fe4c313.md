### Title
Webhook `shop` identity is taken from an unauthenticated header not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value that is handed to app webhook handlers from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `HmacValidator` only covers the raw request body, not this header. Any request whose body+HMAC pair is valid for the app's shared secret will pass verification regardless of what shop domain is claimed in the header, breaking the binding between the authenticated bytes and the shop identity that `WebhookMetadata` reports to the handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/verifies the HMAC solely against that signable string [2](#0-1) . The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` request header with no cryptographic binding to the signature [3](#0-2) .

`Registry.process` accepts a request once `HmacValidator.validate` returns true, then forwards `request.shop` unmodified into `WebhookMetadata`, which is passed to the app's `WebhookHandler#handle` as the trusted shop identity [4](#0-3) . `WebhookMetadata#shop` is a plain `String` field with no further validation [5](#0-4) .

This is exactly the identity-binding gap described in the rules: **a field (`shop`) acted on but not covered by the HMAC**. The equality that should hold is:
`shop bound by HMAC == shop delivered to handler`
but instead the gem enforces only:
`HMAC(raw_body, secret) == received_hmac`, independent of `shop`.

Because Shopify computes webhook HMACs using the single `client_secret` shared by the app across *all* installed shops (not a per-shop secret), a merchant who has installed the app receives their own genuine webhooks (valid body + HMAC signed with the app's `client_secret`). That merchant can replay the exact same body/HMAC pair while substituting the `shopify-shop-domain` header for a different (victim) shop. `HmacValidator.validate` still succeeds (it never inspects the header), and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain, alongside the attacker-controlled body content.

### Impact Explanation
Impact is Critical/cross-tenant: an app that uses `request.shop` (via `WebhookMetadata#shop`) to look up per-shop session/data records or to route webhook side effects, will act on data belonging to shop A while believing it originates from shop B, because the gem presents an unauthenticated header as if it were bound to the verified payload. This is a cross-tenant identity-binding failure originating in the gem's own `Webhooks::Request`/`Registry` code, not merely a documented Shopify behavior the host app chose to ignore — the gem actively packages the unauthenticated header value into the trusted `WebhookMetadata` struct delivered post-HMAC-verification.

### Likelihood Explanation
Likelihood is Low without further verification: exploitation requires the attacker to be a legitimate installer of the target app (to obtain valid body/HMAC pairs signed with the app's shared secret) and to be able to direct a forged HTTP request (with a spoofed shop header) to the app's webhook endpoint before/around the same time the genuine webhook would be delivered, or to know a body that will be accepted meaningfully by the handler for another shop. This requires network-level request forgery capability to the app's webhook receiver, which is plausible for an internet-reachable webhook URL but not trivial. I was not able to verify whether the host application ecosystem (e.g. `shopify_app`) adds any additional shop-header validation on top of this gem, so the real-world exploitability depends on integration details outside `lib/shopify_api/**`.

### Recommendation
Do not treat `Webhooks::Request#shop` as a verified value based solely on HMAC validation of the body. Either incorporate the shop domain header into the signed/verified material, cross-check `request.shop` against a shop known to be associated with the specific `webhook_id`/`topic` via an authoritative source (e.g. an already-stored session/webhook registration keyed by `webhook_id`), or clearly document in `Registry.process`/`WebhookMetadata` that `shop` is unauthenticated header data that must be independently reconciled by the consuming application before being trusted for tenant-scoped operations.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker triggers a webhook event on their own shop and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header (valid, since it's signed with the app's shared `client_secret`).
2. Attacker crafts a new POST request to the app's webhook endpoint reusing the identical body and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [6](#0-5) .
4. `HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC — the forged shop header is never part of the signed data [7](#0-6) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)` [4](#0-3) , causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
