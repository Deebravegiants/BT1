### Title
Webhook shop-tenant identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC of the raw body, but hands the handler a `shop` value taken from an unauthenticated HTTP header. The tenant identity (`shop`) is a field "acted on" by the handler but never covered by the HMAC that is supposed to prove the message's authenticity, mirroring the reported bug class of computing/verifying one thing while acting on a different, unbound value.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` gates everything on `Utils::HmacValidator.validate(request)`, which computes the HMAC solely over that signable string (the body) [2](#0-1) [3](#0-2) . The `shop` value, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the HMAC-covered body [4](#0-3) . After validating the HMAC, `Registry.process` forwards this unauthenticated `shop` field straight into `WebhookMetadata`, which the host app's handler uses to determine the tenant the event belongs to: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [5](#0-4) .

Because the same `api_secret_key` is used to sign webhooks for every shop that has installed a given app, a real attacker can:
1. Install the app on their own (attacker-controlled) shop — an ordinary, unprivileged action.
2. Receive a legitimately signed webhook whose HMAC is valid for the raw body under the app's shared secret.
3. Replay that HTTP request to the app's webhook endpoint while altering the `x-shopify-shop-domain` header to name a victim shop.

The HMAC check still passes (it only verifies the body bytes), so `Registry.process` treats the forged `shop` as authentic and calls the handler with `WebhookMetadata#shop` set to the victim's domain. This breaks the intended identity binding: `shop verified-by-HMAC == shop acted-upon-by-handler`.

### Impact Explanation
Any application logic that trusts `WebhookMetadata#shop` (returned by this gem) as the authenticated tenant for the event — e.g., to look up or mutate per-shop records, apply per-shop side effects, or issue new operations "as" that shop — can be tricked into performing cross-tenant actions using data supplied by an attacker who only controls their own shop's installation. This meets the Critical impact bar of cross-tenant access, since the gem itself hands out a spoofable tenant identifier as if it were authenticated.

### Likelihood Explanation
Likelihood is high: the only precondition is installing the app on an attacker-owned shop (a normal, unprivileged onboarding flow), after which the attacker fully controls the replayed HTTP request's headers, including the shop-domain header, while reusing a validly-signed body.

### Recommendation
Bind the shop identity into the value that is actually verified, e.g. include the `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signable string, or independently verify that the header-derived `shop` corresponds to a shop with an active, known installation/session before passing it to the handler, rather than trusting the header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receiving a legitimate webhook POST with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's `api_secret_key`.
2. Attacker captures this request (body + valid HMAC) and replays it to the app's webhook endpoint, changing only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body bytes against the shared secret [7](#0-6) .
4. The handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, allowing the attacker to inject attacker-chosen webhook data attributed to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
