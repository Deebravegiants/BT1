Found it: `lib/shopify_api/webhooks/request.rb` `to_signable_string` returns only the raw HTTP body, and the `shop` value that identifies the tenant (`x-shopify-shop-domain` header) is read from an unauthenticated header rather than from the HMAC-covered bytes.

### Title
Webhook tenant identity (`shop`) is taken from an HMAC-unverified header, allowing cross-tenant webhook data injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over `@raw_body` only [1](#0-0) , while the tenant-identifying field `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed bytes [2](#0-1) . `Registry.process` validates only the HMAC over the body and then dispatches the handler using the unverified `request.shop` value [3](#0-2) .

### Finding Description
The binding that should hold is: `shop-that-produced-the-HMAC == shop-value-delivered-to-the-handler`. Because `to_signable_string` only returns the raw body, the HMAC proves that Shopify (holder of `api_secret_key`) produced *some* body content for *some* shop, but it proves nothing about which shop header accompanies that body. An attacker who can influence or replay the header layer (e.g., a proxy, gateway, load balancer misconfiguration, or any intermediary that forwards a legitimately-signed webhook payload from Shop A but rewrites/duplicates the `x-shopify-shop-domain` header to Shop B) can cause `Registry.process` to hand the merchant-supplied handler a `WebhookMetadata` object whose `shop` field does not match the shop that actually authorized/signed the payload [4](#0-3) . Since `HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (the body) against the header-derived HMAC value [5](#0-4) , there is no cryptographic binding between `shop` and the signature, unlike the OAuth `AuthQuery`, where `shop` is explicitly included in `to_signable_string` [6](#0-5) .

### Impact Explanation
Downstream host applications rely on `WebhookMetadata#shop` to determine which merchant's data record to update (e.g., look up the shop's session/access token, write to the tenant's row). If the shop identity delivered to the handler can diverge from the shop that actually produced the signed payload, this can result in cross-tenant data mixing inside the consuming app: data for shop A processed under shop B's identity. This maps to the "Critical - cross-tenant access" impact category, since the gem provides no protection against header/body identity divergence and documents `request.shop` as the trusted attribute for tenant dispatch.

### Likelihood Explanation
Exploitation requires an attacker or misconfigured intermediary capable of manipulating headers independently of the body on the path between Shopify and the app (e.g., proxies that don't lock down the `x-shopify-shop-domain` header, or reused/cached request objects), which is a narrower vector than a fully unauthenticated remote attacker directly hitting the app with fabricated headers (since a completely fabricated header+bogus body would still need a valid HMAC over that body). This is a real architectural gap but likelihood is lower than a straightforward auth bypass — it depends on infrastructure that does not treat body and headers atomically.

### Recommendation
Include the `shop` (and other trust-relevant headers such as `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or independently verify the `shop` header value against an expected/known-active shop list before dispatching to handlers, mirroring how `AuthQuery#to_signable_string` includes `shop` explicitly.

### Proof of Concept
Conceptual (cannot be fully demonstrated without a live intermediary, since this gem's own HTTP entrypoint is instantiated by the host app from raw headers/body):
1. Shopify sends a legitimately signed webhook for `shop-a.myshopify.com` with body `{"id":1}` and a valid `x-shopify-hmac-sha256`.
2. An intermediary/proxy in the request path (or a bug in the host framework header handling) forwards the same signed body but with `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts this combination unmodified [7](#0-6) .
4. `Registry.process` validates the HMAC (which only checks the body) successfully, then calls the handler with `shop: request.shop` == `"shop-b.myshopify.com"` even though the payload was authorized for `shop-a` [8](#0-7) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
