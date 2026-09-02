This confirms the vulnerability path: `Registry.process` verifies only the HMAC of the raw body via `Utils::HmacValidator.validate(request)`, then trusts `request.shop` (from the `shopify-shop-domain` HTTP header) as the tenant identifier passed into `WebhookMetadata`, which apps use to route/attribute the webhook data (per `docs/usage/webhooks.md` example: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`).

### Title
Webhook tenant identity (`shop` domain) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  , which is the sole input verified by `Utils::HmacValidator.validate` in `Registry.process` [2](#0-1) . The `shop` domain, however, is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [3](#0-2) , and is forwarded verbatim into `WebhookMetadata.shop`, which the gem's own documentation shows apps using to key/attribute the webhook to a specific tenant [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop` (the tenant the webhook body is attributed to) == `shop` (the tenant that the HMAC-secret-holder actually signed for). Instead, the code only proves `HMAC(raw_body) == valid` and then separately and unconditionally trusts a header value for `shop`, so the equality actually enforced is only `hmac(body)==valid`, with no equality constraint at all between `body` and `shop`.

Because the webhook secret is the app's single, shared `api_secret_key` (not a per-shop secret) [5](#0-4) , any Shopify merchant who has genuinely installed the app receives real webhooks from Shopify with a correctly computed HMAC over their own body. Since the header carrying the shop domain is excluded from the signed content, that merchant (an unprivileged, low-cost actor — just another shop that installed the app) can replay the exact `raw_body`+`hmac` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` still passes because it never inspects the header, and `Registry.process` hands the handler a `WebhookMetadata` claiming the attacker-controlled body originated from the victim shop [2](#0-1) .

### Impact Explanation
This breaks the tenant boundary that host apps rely on this gem to enforce ("the shop authenticated" vs. "the shop the data is attributed to"). Any application that uses `data.shop` to select which merchant's database record/session to update (exactly as the gem's own documented example does) can be made to write attacker-supplied webhook payloads into a completely different, victim merchant's data — a cross-tenant data injection achieved purely by an unprivileged installer of the app, with no access token or secret required.

### Likelihood Explanation
Likelihood is high for any app that installs the recommended pattern from `docs/usage/webhooks.md` and processes the webhook body without independently correlating `data.shop` against `data.body`'s own shop/domain fields. All the attacker needs is to be able to install the app on any one shop (a normal, unprivileged act) and be able to send an arbitrary HTTP request to the app's public webhook endpoint with a modified header.

### Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) inside the HMAC-signable content, or otherwise cryptographically bind the header value to the signed body (e.g., by validating it against the `X-Shopify-Shop-Domain` claim through a per-shop-registered value instead of trusting the header) so `to_signable_string` cannot be satisfied by a replayed body under a spoofed shop header.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a genuine webhook (e.g., `orders/create`) and capture the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Send a new POST to the app's public webhook endpoint with the same body `B` and same header `H`, but with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not binding) [6](#0-5) ; `Utils::HmacValidator.validate` succeeds because it only recomputes HMAC over `B` [7](#0-6) .
4. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)` [8](#0-7) , causing the app to attribute attacker-controlled data to the victim tenant.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
