This confirms the vulnerability. `WebhookHandler#handle` receives `WebhookMetadata` whose `shop` field [1](#0-0) is populated from `request.shop` in `Registry.process` [2](#0-1) , and host apps use that `shop` value as the tenant identifier to route/persist webhook data — yet `Request#hmac` is validated only over `to_signable_string`, which returns just `@raw_body` [3](#0-2) , so the `shop-domain` header is never covered by the HMAC.

### Title
Webhook `shop-domain` header is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, excluding the `shop-domain` (and `topic`/`webhook-id`) headers. `HmacValidator.validate` therefore only proves that the *body* bytes were signed by Shopify with the app's `api_secret_key`; it proves nothing about which shop the payload is attributed to. Any holder of one genuine, validly-signed webhook delivery (e.g., from their own store where they installed the app) can resubmit that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, and the signature will still validate.

### Finding Description
The binding that should hold is:

`shop_the_HMAC_authenticates == shop_the_handler_acts_on`

but in this gem it is:

`shop_the_HMAC_authenticates = ∅ (not covered) ≠ request.shop (attacker-controlled header)`

- `HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field [4](#0-3) .
- For `Request`, `to_signable_string` returns only `@raw_body`; `shop`, `topic`, `webhook_id`, and `api_version` are all read from separate, unauthenticated headers [5](#0-4) .
- `Registry.process` validates the HMAC and then dispatches to the registered handler using `request.shop` taken straight from that unauthenticated header [2](#0-1) .
- Consuming applications are expected to trust `WebhookMetadata#shop` as the tenant/store identifier for the event [6](#0-5) .

Because the same `api_secret_key` is shared across every shop that installs the app, an unprivileged user can install the app on their own store, capture one legitimate `(raw_body, hmac)` pair delivered to the app's public webhook endpoint, and replay it with a forged `x-shopify-shop-domain` header naming a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspected the shop header, and the handler will process the event as if it originated from the victim's store.

### Impact Explanation
This crosses a tenant boundary: a payload the app believes came from Shop B can actually be fully attacker-controlled in its shop attribution while remaining "cryptographically validated." Depending on the handler's use of `data.shop` (e.g., writing/deleting records keyed by shop, triggering `shop/redact` or `customers/data_request` compliance flows, updating billing/subscription state), this enables cross-tenant data corruption or disclosure using only a signature obtained from the attacker's own tenant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to have received at least one genuine webhook for any shop using the app (trivial: install the app for free on any store) and to be able to POST directly to the app's webhook endpoint with custom headers (no Shopify-side interception needed, since the endpoint is a normal public HTTP endpoint). No access token, `client_secret`, or privileged account is required — only replaying already-observed bytes with a modified header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signable payload the gem verifies, or otherwise cryptographically bind the declared shop to the request before dispatching to handlers — e.g., require the `shop-domain` header to match a shop the caller has verified via a separate authenticated channel, or extend `to_signable_string` to incorporate the shop header so cross-tenant replay changes the signature.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) to receive a genuine delivery with body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S`).
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same raw body `B`, the same `x-shopify-hmac-sha256: H` header, but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully [7](#0-6) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H`, so validation passes [8](#0-7) .
5. The registered handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, believing this event is authentically from the victim shop, even though only the attacker's own signature was ever verified.

### Citations

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-23)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
