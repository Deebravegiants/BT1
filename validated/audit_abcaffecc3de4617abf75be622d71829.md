Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC over that signable string and then dispatches to the handler using the header-derived `shop` value with no further check that it matches the body content [3](#0-2) .

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Registry.process` and forwarded to the app's `WebhookHandler` come from `shopify-*`/`x-shopify-*` HTTP headers that are never part of the HMAC-verified bytes [2](#0-1) . This breaks the intended binding of "bytes verified" (the body) versus "bytes parsed for identity" (the headers).

### Finding Description
`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field using `OpenSSL.secure_compare` [4](#0-3) . For webhooks, `to_signable_string` is defined as just `@raw_body` [1](#0-0) ; the `shop`, `topic`, and `webhook_id` accessors that identify *which tenant and event* the payload belongs to are pulled straight from headers with no cryptographic binding to those headers at all [2](#0-1) .

Any entity that can install the app on their own (unprivileged) shop receives real webhook deliveries signed with the app's shared `client_secret` HMAC key — that signature is over the body only. Because the shop-domain and topic headers are not covered by that signature, an attacker who controls where requests are sent to the app's own webhook endpoint (i.e., the host application's webhook controller, which per this gem's documented usage simply forwards `request.raw_post` and `request.headers` into `ShopifyAPI::Webhooks::Request.new` and calls `Registry.process`) can replay a validly-signed `(raw_body, hmac)` pair captured from their own shop while substituting an arbitrary `shopify-shop-domain` header. `Registry.process` only checks the HMAC of the body [5](#0-4) , then builds `WebhookMetadata` using `request.shop` taken from the spoofed header [6](#0-5) , and dispatches it to the handler as if it genuinely originated from that other shop.

The equality that should hold is: `shop authenticated by HMAC == shop acted upon by the handler`. Here, the HMAC authenticates only the body bytes, while the shop identity acted upon comes from an unauthenticated header, so the two are decoupled.

### Impact Explanation
An application relying solely on this gem's `HmacValidator.validate(request)` result to trust `request.shop` (as the documented usage pattern in `docs/usage/webhooks.md` suggests — construct `Request` from raw headers/body and call `Registry.process`) can be tricked into attributing a legitimately-signed payload to a different merchant/tenant than the one it actually came from. This is a cross-tenant identity confusion: data, redaction requests, or business events processed for shop A's payload get applied under shop B's identity, without the attacker needing any of shop B's credentials.

### Likelihood Explanation
Medium: the attacker needs to be a legitimate (even if low-privilege) merchant who has installed the public app to obtain one genuine `(raw_body, hmac)` pair, and needs the ability to send crafted HTTP requests directly to the app's webhook endpoint (bypassing Shopify's delivery, which the gem does not prevent since `Request.new` accepts arbitrary caller-supplied headers/body). No secret key or elevated credential is required.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`) in the signable string/HMAC computation for webhooks, or independently verify (e.g., via a stored session/shop registry) that the shop derived from the header actually corresponds to the signing key/tenant before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the public app on `attacker-shop.myshopify.com`; Shopify sends a real webhook to the app's endpoint with body `raw_body` and header `shopify-hmac-sha256` = HMAC-SHA256(`raw_body`, app's `client_secret`) — valid per `HmacValidator.validate` [7](#0-6) .
2. Attacker captures this `(raw_body, hmac)` pair.
3. Attacker POSTs directly to the app's webhook route with the same `raw_body`/`hmac` but sets `shopify-shop-domain: victim-shop.myshopify.com` (and any `topic`/`webhook-id` of their choosing).
4. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) [8](#0-7) ; `Registry.process` validates the HMAC successfully (it only checks the body) and invokes the handler with `shop: "victim-shop.myshopify.com"` [3](#0-2) , causing the app to process attacker-controlled data under the victim shop's identity.

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
