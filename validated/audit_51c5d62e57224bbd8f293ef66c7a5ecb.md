### Title
Webhook `shop` (tenant) header is not covered by the HMAC signature, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, but the `shop` value that the handler uses to attribute the webhook to a tenant is taken from an HTTP header that is never included in that signature. This breaks the intended binding of "authenticated bytes" to "the shop the payload is attributed to."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` accepts the request as authentic once `Utils::HmacValidator.validate(request)` succeeds against that signable string [2](#0-1) . The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic tie to the signed body [3](#0-2) . The same is true for `topic`, `api_version`, and `webhook_id` [4](#0-3) .

`HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it to the supplied `hmac` value [5](#0-4) . Because the signature is only a function of `@raw_body`, it is identical for any combination of headers sent alongside that body. Once `process` confirms the signature, it immediately forwards `request.shop` to the registered handler as the tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) .

The binding that should hold is:
`shop_claimed_by_headers == shop_that_produced_the_signed_bytes`

Because `shop` is outside the signable string, this equality is never checked — only `HMAC(secret, raw_body)` is verified, independent of `shop`.

Contrast this with the OAuth callback path, where every field that is later trusted (`code`, `host`, `shop`, `state`, `timestamp`) is explicitly included in `AuthQuery#to_signable_string` and thus covered by the HMAC [7](#0-6) . The webhook path lacks the analogous protection for the `shop` field that callers rely on for tenant attribution.

### Impact Explanation
Any party who can obtain one legitimate webhook body + valid HMAC for their own store (trivial: install the app on a free/dev store they control and capture the webhook Shopify sends them, or capture their own webhook traffic) can resend that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value naming a victim shop. `Registry.process` will accept the request as authentic (the HMAC still matches the unchanged body) and dispatch it to the app's handler tagged with the attacker-chosen `shop` [2](#0-1) . Any host application that keys persistence, authorization, or session/data lookups off `WebhookMetadata#shop` (as the gem's own documentation and the `shop`-scoped design of `Session`/webhook processing implies) will store or act on attacker-controlled data under the wrong tenant — a cross-tenant data injection/confusion condition.

### Likelihood Explanation
High. No secret, access token, or privileged account is required — only the ability to install/operate one shop (attacker's own) and issue a raw HTTP POST with modified headers to the target app's public webhook endpoint. The attack is cheap and repeatable.

### Recommendation
Include the tenant-identifying header (`shop-domain`) — and ideally `topic`/`webhook-id` — in the signable content actually verified, or otherwise cryptographically bind them to the body before trusting `request.shop`. At minimum, document/require host applications to cross-check `request.shop` against an independently known/authorized shop for the webhook subscription (e.g., verify it corresponds to a `webhook_id` previously registered by the gem for that shop) rather than trusting the header on its own once HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate webhook, e.g. `orders/create`. They capture the raw POST: `raw_body` and header `X-Shopify-Hmac-Sha256: <hmac>`.
2. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` accepts the request (all required headers present) [8](#0-7) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unchanged from step 1 — and returns `true` [9](#0-8) .
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's order data>)`, causing the host app to associate attacker-controlled content with the victim tenant [10](#0-9) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
