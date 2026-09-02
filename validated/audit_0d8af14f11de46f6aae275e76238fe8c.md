### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant confusion - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain` header, but the HMAC that `Registry.process` validates only covers the raw request body, never the shop header. Any party able to produce one request with a body/HMAC pair that passes validation can pair that valid `(raw_body, hmac)` with an arbitrary `shop-domain` header value, and `Registry.process` will accept it and dispatch it to the app's handler under the attacker-chosen shop identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed bytes [2](#0-1) . `Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` and compares it to the `hmac` header value [3](#0-2) . `Registry.process` performs exactly this check and, once it passes, unconditionally forwards `request.shop` to the handler as the tenant identity for the webhook payload [4](#0-3) .

This breaks the intended identity binding `authenticated(body) == identity(shop)`: the gem authenticates the bytes of the body but not the shop the body is attributed to. Any request whose body/HMAC pair validates (e.g., a genuinely delivered webhook for the attacker's own shop, since HMAC-SHA256 with the shared `client_secret` only depends on the body) can be replayed to the host application's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim's `myshopify` domain. `HmacValidator.validate` still returns `true` because it never inspects that header, so `Registry.process` treats the forged shop identity as authenticated and dispatches it to `handler.handle` as if it were verified.

### Impact Explanation
This is a cross-tenant identity confusion at the boundary the gem is responsible for authenticating. Host applications rely on `WebhookMetadata#shop` (built from `request.shop`, passed after only an HMAC check) as the trusted tenant key to route data (e.g., attaching an order/customer payload to the wrong merchant, or triggering `shop/redact`/`customers/redact`/`customers/data_request` compliance actions against a shop the payload didn't originate from). Because the shop field crossing this trust boundary is never bound to the authenticated bytes, this can produce cross-tenant data leakage or corruption — Critical impact per the scope's classification of cross-tenant access.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(raw_body, hmac)` pair signed with the app's real `client_secret` — trivially obtainable by any merchant who installs the target app and receives one legitimate webhook to their own shop (no privileged credentials or the `client_secret` itself are needed). They then replay that same body/HMAC to the app's public webhook HTTP endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. This is fully reachable by any unprivileged internet-capable merchant, without needing TLS interception, leaked secrets, or social engineering.

### Recommendation
Bind the shop identity to the authenticated bytes: include the `x-shopify-shop-domain` (and ideally `topic`, `webhook-id`) header values in `to_signable_string`, or independently verify that the shop derived from the header matches an expected/registered shop before trusting `WebhookMetadata#shop` in `Registry.process`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`, causing Shopify to send a legitimate webhook with a valid `x-shopify-hmac-sha256` for the raw body and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture the raw body and the valid HMAC header value.
3. Replay the same raw body and HMAC to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) [5](#0-4) ; `HmacValidator.validate` returns `true` because the HMAC still matches the unchanged body [6](#0-5) ; `Registry.process` dispatches the handler with `shop: request.shop` equal to `victim.myshopify.com` [4](#0-3) , even though the payload never actually originated from that shop.

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
