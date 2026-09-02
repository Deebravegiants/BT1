This confirms the asymmetry: `AuthQuery#to_signable_string` (OAuth callback) explicitly binds `shop`, `code`, `host`, `state`, `timestamp` into the HMAC-signed string, while `Webhooks::Request#to_signable_string` only returns `@raw_body`, leaving the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers completely outside the HMAC computation.### Title
Webhook `shop` (and `topic`/`webhook-id`) attribution is not bound by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating that the HMAC covers the raw request body [1](#0-0) . The `shop` (and `topic`/`webhook_id`) values that are handed to the app's handler and used to attribute the event to a specific merchant come from HTTP headers that are never included in the signed content [2](#0-1) . This breaks the intended identity binding `hmac == HMAC(secret, body ‖ shop ‖ topic ‖ webhook_id)`; the gem effectively verifies `hmac == HMAC(secret, body)` only, while `shop` is parsed but never verified.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` with: [3](#0-2) 

`to_signable_string` returns only `@raw_body`; the `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from unauthenticated headers (`shopify-shop-domain`, `shopify-topic`, etc.) with no relation to the HMAC.

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares to the `hmac` header [4](#0-3) . Since `to_signable_string` is just the body, the signature is valid for that body regardless of what the `shop-domain` header says.

`Registry.process` then uses the *unverified* `request.shop` (and `topic`, `webhook_id`) to build `WebhookMetadata` and dispatch to the app-registered handler: [1](#0-0) [5](#0-4) 

This is a direct architectural contrast with the OAuth callback path in the same gem, where `Oauth::AuthQuery#to_signable_string` explicitly folds `shop` (along with `code`, `host`, `state`, `timestamp`) into the signed string before HMAC validation [6](#0-5) , showing the gem knows how to bind an identity field into the signature when it matters, but did not do so for webhook `shop`.

The documentation directs app authors to trust `data.shop` from `WebhookMetadata` as the attribution key for the event without further verification, reinforcing that the library's own contract treats it as authenticated: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook" [7](#0-6) , and the example handler uses `data.shop` directly as the shop-domain key for downstream processing [8](#0-7) .

**Break-the-binding equality:** the security-relevant equality that should hold is:
`hmac_header == HMAC(secret, body, shop)` (shop cryptographically bound to the payload)

What actually holds is:
`hmac_header == HMAC(secret, body)` and `shop == <unauthenticated header value>`

An attacker who is any one of the app's own installed merchants (an "unprivileged" tenant relative to other tenants of a multi-tenant app) receives real webhooks from Shopify for their own store, each with a body and a valid HMAC computed from the shared `client_secret`. Because the shop identity is not part of the signed content, that same `(raw_body, hmac)` pair remains valid if replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header changed to name a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This crosses a tenant boundary: a malicious merchant tenant can forge webhook events that are dispatched to the app's handler as though they originated from a different, victim merchant's shop, while still passing the gem's `Errors::InvalidWebhookError` HMAC check [9](#0-8) . Depending on how the host app's handler uses `data.shop` (e.g., to look up a session/store record and write data, as shown in the documented example calling `perform_later(shop_domain: data.shop, ...)`), this enables cross-tenant data injection/confusion — writing attacker-controlled order/product/app data under another merchant's shop identity. This matches the "cross-tenant access" Critical impact category, since the vulnerability is rooted in this gem's own webhook-authentication primitive (`Webhooks::Request` / `HmacValidator` / `Registry.process`), not merely a host application choosing to ignore documented behavior — the documented API itself asserts that `process` "verif[ies] the request did indeed come from Shopify," which is only true for the body, not for `shop`/`topic`/`webhook_id`.

### Likelihood Explanation
Any shop that has installed the app (a normal, unprivileged tenant with no special access to `api_secret_key` or another shop's credentials) can trigger their own legitimate webhook (e.g., by updating any resource covered by a subscribed topic), capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair by controlling their own webhook receiving endpoint/proxy, and replay it to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header. No secret material or privileged access is required beyond being an ordinary app-installing merchant, and the replay/header-forgery only requires a normal HTTP client.

### Recommendation
Bind the routing/attribution fields into the signed content, mirroring the `AuthQuery` pattern: include `shop`, `topic`, and `webhook_id` in `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them, e.g. via a MAC over `shop|topic|webhook_id|body`), so that `HmacValidator.validate` fails if any of these headers are altered relative to what Shopify actually signed. At minimum, document and/or enforce that `WebhookMetadata.shop` must be cross-checked by the caller against a known, previously established session/store record before being trusted for any tenant-scoped action.

### Proof of Concept
1. App has topic `orders/create` registered, and shop `attacker.myshopify.com` has installed it.
2. Shopify sends a legitimate webhook to the app for `attacker.myshopify.com`:
   - headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`
   - body: `{"id": 1, ...}`
3. Attacker controls their own endpoint/logs and captures `(body, hmac)`.
4. Attacker (or a script under their control) sends a new HTTP POST to the same app webhook endpoint with the **identical** `body` and `hmac`, but `x-shopify-shop-domain: victim.myshopify.com`.
5. `Webhooks::Request.new` parses headers/body as usual [10](#0-9) ; `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, body)` — identical to the original, so validation passes [9](#0-8) .
6. `handler.handle` is invoked with `WebhookMetadata(shop: "victim.myshopify.com", topic: "orders/create", body: {...}, ...)` [11](#0-10)  — the app now processes attacker-supplied data as if it belongs to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
