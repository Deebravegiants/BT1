I have confirmed the core finding: the webhook HMAC signature covers only the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` identity field consumed by `Registry.process` and exposed to the handler via `WebhookMetadata.shop` comes from an unsigned HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`).### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body [1](#0-0) , while the `shop` value that `Registry.process` trusts and forwards to the app's webhook handler is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string` — i.e. the body bytes — and never binds the `shop` header into that computation [3](#0-2) . `Registry.process` then uses `request.shop` as the tenant identity handed to the app-supplied handler without any additional check [4](#0-3) .

### Finding Description
The equality this code is supposed to guarantee is:
`shop identity trusted by the handler == shop identity that Shopify cryptographically attested when producing the HMAC`

In `HmacValidator.validate_signature`, the received HMAC is compared against a signature computed over `verifiable_query.to_signable_string` [3](#0-2) . For webhooks, `to_signable_string` is defined as simply `@raw_body` [1](#0-0) , meaning the HMAC secret only authenticates the JSON payload bytes — nothing about which shop the payload belongs to. The `shop` accessor used elsewhere in the pipeline is read straight out of request headers, which are not part of the signed material at all: `shopify_header("shop-domain")` [2](#0-1) .

`Registry.process` validates the HMAC (`Utils::HmacValidator.validate(request)`) and, if it passes, immediately builds `WebhookMetadata` using `request.shop` from the header and dispatches it to the registered `handler.handle` [4](#0-3) . Documentation confirms that `shop` in `WebhookMetadata` is meant to be an authenticated indicator of which merchant the event belongs to, and that host apps are expected to use it directly (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) . Since the header is not covered by the signature, any request bearing a body+HMAC pair that is valid under the app's shared `api_secret_key` can be replayed with an arbitrary `shopify-shop-domain` header and will still pass `HmacValidator.validate`, attributing the (attacker-controlled) shop value to that payload.

Because the HMAC secret (`api_secret_key`) is the same for every shop that installs a given app, any merchant who legitimately installs the app receives real, validly-signed webhooks for their own store. Such a merchant (an "unprivileged internet user" with respect to any other tenant of the same app) can capture one of these valid `(body, hmac)` pairs and resend it directly to the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` will accept it because it never inspects the header, and `Registry.process` will hand the handler `shop: <victim-shop>` together with the attacker-chosen body.

### Impact Explanation
This breaks the tenant boundary the gem is documented to provide via `WebhookMetadata#shop`: an attacker who only controls their own shop's installation of a third-party app can inject webhook events that the app attributes to a different merchant's shop. Depending on how the host application uses `data.shop` (e.g., to select which merchant's session/access token to act on, write data into a per-shop store, or trigger shop-scoped side effects), this can lead to cross-tenant data corruption or actions taken against a victim shop's resources without ever compromising the victim's credentials — matching the "cross-tenant access" Critical impact criterion.

### Likelihood Explanation
Exploitation only requires: (1) the attacker to be a legitimate merchant/installer of the target app (an unprivileged install, not a privileged account of the app or Shopify), (2) capturing one benign, validly-signed webhook body sent to their own installation, and (3) replaying it against the app's public webhook endpoint with a modified `shop` header. No knowledge of `api_secret_key`, access tokens, or any victim credential is required. This is a mechanical, deterministic exploitation path once the shared HMAC secret is known implicitly through normal, legitimate use of the app by the attacker's own store.

### Recommendation
Bind the shop identity into the signed material, or independently verify it: either compute/require the HMAC over `raw_body + shop-domain header` (matching what a per-shop secret model would need), or — more consistent with Shopify's actual model — treat the `shop` header purely as a hint and enforce that the host application look up the expected shop for that `webhook_id`/subscription out-of-band (e.g., cross-check against Shopify's webhook subscription registration or an app-side shop mapping) rather than trusting the header value as an authenticated identity in `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1}"` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body bytes against the HMAC [7](#0-6) .
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "victim-shop.myshopify.com"` and invokes the host app's handler, which will process/act as if the event genuinely originated from the victim shop [8](#0-7) .

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
