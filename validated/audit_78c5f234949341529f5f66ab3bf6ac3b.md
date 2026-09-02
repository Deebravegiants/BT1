### Title
Webhook `shop`/`topic`/`webhook_id`/`api_version` fields are trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the HMAC-signable content solely from the raw body, while the `shop`, `topic`, `webhook_id`, and `api_version` values that are passed downstream to the app's webhook handler (and used for per-tenant routing/action) are read straight from unauthenticated HTTP headers. This breaks the identity binding `bytes verified == bytes acted on`, allowing a replayed, validly-HMAC'd webhook body to be relabeled with an arbitrary `shop` domain.

### Finding Description
`Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, which computes the HMAC exclusively over `request.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` — the fields that are actually acted upon by `Registry.process` to build `WebhookMetadata` and dispatch to the app's handler — are parsed directly out of caller-controlled HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.), none of which are included in the HMAC computation: [3](#0-2) [4](#0-3) 

`Registry.process` only checks the HMAC and then forwards these unauthenticated header values straight to the app: [5](#0-4) 

The gem's own documentation instructs integrators to use `data.shop` as the tenant key for downstream processing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), confirming that `shop` is treated as an authenticated tenant identifier by design, even though it is never covered by the signature: [6](#0-5) 

This is the same class of bug as the reported analog: an action (tenant attribution / routing) is performed based on a field (`shop`) that is not covered by the integrity check (HMAC over body only), so the verified bytes ≠ the bytes acted on.

### Impact Explanation
Any party capable of obtaining one validly-signed webhook body+HMAC pair for their own (attacker-controlled) shop can resend that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. Since the gem never validates that the header-derived `shop` is consistent with anything cryptographically bound to the payload, the host application — following the gem's documented usage pattern — will process the webhook as if it originated from the victim tenant. This is a cross-tenant confusion vector: attacker-controlled or replayed webhook data gets attributed to and acted on for a different merchant's shop, which is a cross-tenant access impact.

### Likelihood Explanation
Exploitability requires only network access to the app's public webhook endpoint and possession of one legitimately signed webhook (trivially available to an attacker who operates their own test/dev shop with the same app installed, since Shopify signs webhooks per-app-secret, not per-shop). No access token, `client_secret`, or privileged credentials are needed. This is a realistic and directly reachable scenario for any developer building on top of this gem using its documented API.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable string, or otherwise cryptographically bind them to the verified payload, so `HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually signed. At minimum, document prominently that `data.shop` and other header-derived fields are not integrity-protected and must not be used as an authoritative tenant identifier without independent verification (e.g., cross-checking against a known/stored shop for the webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a real webhook from Shopify: body `B`, header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the same raw body `B` and same `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `to_signable_string` (= `B`) — this matches `H`, so validation passes: [7](#0-6) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the host app (per the gem's documented pattern) processes/enqueues work attributed to `victim.myshopify.com`, even though the payload never originated from or was authorized for that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
