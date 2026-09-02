This confirms the finding: the docs explicitly promise that `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and the sample handler trusts `data.shop` to route/attribute the webhook to a specific merchant [2](#0-1) , but the HMAC signature only covers the raw body, not the `shop` (or `topic`/`webhook_id`) header.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to tell the host application which merchant/tenant the webhook belongs to.

### Finding Description
`Registry.process` calls `Utils::HmacValidator.validate(request)` to authenticate the request, then immediately passes `request.shop` into `WebhookMetadata` for the handler: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [4](#0-3) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — it does not include `shop`, `topic`, `webhook_id`, or `api_version`, all of which are read straight from unauthenticated HTTP headers: [5](#0-4) [6](#0-5) 

This is the same bug class as the report's `claimed[][]`-vs-transferred-balance mismatch: an identity/ownership field (`shop`) is *acted upon and forwarded to the handler* but is *not covered by the cryptographic check* (`hmac`) that is supposed to authenticate the whole request. The equality that should hold — `shop asserted in header == shop cryptographically bound to the signed payload` — does not hold, because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that has installed the app, not shop-specific.

### Impact Explanation
Because the same `client_secret` produces valid HMACs for every shop's webhook traffic to this app, a merchant who has installed the app (an "unprivileged" party with respect to any other merchant on the same app) can capture a legitimate `(raw_body, hmac)` pair from a webhook delivered to their own store, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` claiming the (attacker-controlled) body belongs to the victim's shop. As the docs themselves instruct developers to key their persistence/business logic off `data.shop` (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)`), a host app following the documented pattern will process attacker-supplied data under another tenant's identity — a cross-tenant data/action confusion.

### Likelihood Explanation
Exploitation requires only that the attacker be a real, existing installer of the target app (routine, unprivileged access — no `api_secret_key`, no access token, no leaked credentials, no TLS interception needed) and the ability to POST an HTTP request with attacker-chosen headers to the app's own public webhook endpoint, which by design must accept unauthenticated inbound HTTP requests from "Shopify". The library provides no defense against this because it never binds `shop` to the signature.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-covered signable content, or otherwise require the caller to independently pin/allowlist the expected shop per registered webhook path/session before trusting `request.shop`, so that the header used to attribute a webhook to a tenant is the same value protected by `Utils::HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) so Shopify POSTs a legitimate `(raw_body, x-shopify-hmac-sha256)` pair to the app's webhook endpoint.
2. Attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally [7](#0-6) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes HMAC over `raw_body` [8](#0-7) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, and, following the documented pattern, persists/acts on this data as if it genuinely originated from the victim's store.

### Citations

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
