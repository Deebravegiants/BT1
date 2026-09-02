This confirms the finding: the webhook HMAC only signs `@raw_body` [1](#0-0)  while `topic`, `shop`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1)  and passed straight into the handler without any cross-check against the body's actual origin [3](#0-2) .

### Title
Webhook shop-domain header is not bound by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature (`to_signable_string`) purely from the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are never included in that signed string. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then trusts the header-derived `shop` value when constructing `WebhookMetadata` passed to the app's handler.

### Finding Description
`Utils::HmacValidator.validate` verifies `HMAC-SHA256(secret, verifiable_query.to_signable_string) == received_hmac` [4](#0-3) . For webhooks, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from the `shopify-*`/`x-shopify-*` headers with no cryptographic binding to the body or to each other [2](#0-1) .

`Registry.process` raises only if the body HMAC fails, then immediately builds `WebhookMetadata` using `request.shop` (the unauthenticated header) and hands it to the app-supplied handler [3](#0-2) . Documentation confirms handlers are expected to trust `data.shop` for tenant-scoped actions such as enqueuing per-shop jobs [5](#0-4) .

This breaks the identity binding: `hmac_valid_for(raw_body)` is treated as proof that `(shop, topic, webhook_id, body)` all originated together from Shopify for that specific shop, but the gem only proves the body bytes were HMAC'd with the app's secret — it proves nothing about which shop, topic, or webhook_id the signer intended.

### Impact Explanation
An attacker who owns any shop that has this app installed (or otherwise obtains one genuine, Shopify-signed webhook body+HMAC pair for a given raw body, e.g. from their own store's webhook deliveries) can replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) headers to name a different, victim shop. Because none of these headers are covered by the signature, `HmacValidator.validate` still succeeds, and the app's handler processes attacker-controlled body content under the victim shop's identity. Any app logic that uses `data.shop` to look up sessions, write per-tenant data, or trigger tenant-scoped side effects can be tricked into acting on a different tenant than the one that actually signed the request — a cross-tenant data confusion condition.

### Likelihood Explanation
Medium-to-high: exploitation only requires the attacker to run/own a single shop with the app installed (a normal, unprivileged user action) and to be able to send arbitrary HTTP requests to the app's public webhook endpoint with custom headers — no access token, `client_secret`, or `api_secret_key` is needed. The attacker never needs to compute a forged HMAC; they simply reuse the legitimate one issued for their own shop's webhook.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the body), or independently verify that the `shop-domain` header matches a shop for which the app has an active, previously-established session/installation before dispatching to the handler. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are unauthenticated and must be revalidated by the host app against known installed shops before being trusted for tenant-scoped logic.

### Proof of Concept
1. App installs webhook handler trusting `data.shop` for per-tenant actions, per the documented pattern [5](#0-4) .
2. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with body `B`; Shopify sends `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, HMAC(secret,B))` and replays it to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-webhook-id`/`x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers since only `hmac-sha256`, `topic`, and `shop-domain` presence is checked [6](#0-5) ; `Registry.process` validates `HmacValidator.validate(request)` against `B` only, which passes, and dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` to the handler [7](#0-6) .
5. The handler performs tenant-scoped work believing it originated from `victim-shop`, achieving cross-tenant data confusion without ever needing `victim-shop`'s credentials.

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
