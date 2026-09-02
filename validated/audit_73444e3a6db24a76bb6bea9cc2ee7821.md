Confirmed: `Utils::VerifiableQuery#to_signable_string` is the only value fed into the HMAC computation, and for webhooks, `Webhooks::Request#to_signable_string` returns solely `@raw_body`, while `Webhooks::Request#shop` and `#topic` are pulled from headers that are never part of that signable string.This confirms the flow: `Registry.process` validates the HMAC using only `request.topic` selection and `HmacValidator.validate(request)`, then passes `request.shop` (an unauthenticated header value) directly into `WebhookMetadata` and on to the host app's `WebhookHandler#handle`.### Title
Webhook `shop-domain` Header Not Covered by HMAC Allows Cross-Tenant Webhook Forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which in turn only checks the HMAC over `request.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns exclusively the raw request body [1](#0-0) . The `shop` (and `topic`) values used downstream are read straight from HTTP headers that are never included in the signed bytes [2](#0-1) . `Registry.process` then forwards this unauthenticated `shop` value directly into `WebhookMetadata`, which is handed to the host app's `WebhookHandler#handle` [3](#0-2) [4](#0-3) .

### Finding Description
The binding that should hold is:
`shop attributed to the webhook == shop that produced the HMAC-signed bytes`

`HmacValidator.validate` computes `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` and compares it only against the received HMAC [5](#0-4) . For webhooks, `to_signable_string` is defined as `@raw_body` alone [1](#0-0) , while `shop` is pulled from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signable string and is thus not bound to the signature at all [2](#0-1) .

Attack sequence:
1. Before the attack: a legitimate webhook for the attacker's own shop (`attacker-shop.myshopify.com`) arrives with body `B` and a valid `hmac = HMAC(secret, B)`. This is a real, correctly-signed message the attacker legitimately possesses (installing the app on their own store yields real webhook deliveries with valid signatures).
2. After the attack: the attacker resends the exact same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but substitutes the `shop-domain` header with `victim-shop.myshopify.com`.
3. `HmacValidator.validate` still succeeds, because it only checks `HMAC(secret, raw_body)`, and `raw_body` is unchanged — the shop header was never part of the check [6](#0-5) .
4. `Registry.process` raises no error, looks up the handler by topic, and invokes `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop` now equal to `victim-shop.myshopify.com`, an identity the signature never vouched for [3](#0-2) .

The host application's webhook handler — which is expected by this gem's documented contract to trust `WebhookMetadata#shop` as an authenticated tenant identifier once `Registry.process` succeeds — will process attacker-controlled body content under the victim shop's identity.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographically verified payload and the shop the application attributes it to, enabling cross-tenant data injection: an attacker can cause the app to process forged events (e.g., order/customer/product data-affecting webhooks such as `customers/data_request`, `orders/create`, `app/uninstalled`) as if they originated from any victim shop, since the only field naming the tenant (`shop-domain` header) carries no cryptographic binding. Depending on how the host app's `WebhookHandler` implementations use `data.shop` (e.g., to look up sessions, trigger data deletion/exports, or update per-shop state), this can result in cross-tenant state corruption or unauthorized actions performed against a shop the attacker does not control.

### Likelihood Explanation
Likelihood is high for any app that has legitimately installed the gem's webhook processing and has at least one shop under attacker control (trivial for any developer who can install their own app, which is the normal case for third-party embedded apps). No access to `api_secret_key`, tokens, or victim credentials is required — only a validly-signed payload from the attacker's own tenant, which is routinely delivered to the attacker's own endpoint by Shopify.

### Recommendation
Bind the shop identity to the signed content: include the `shop-domain` header value in the signable string used by `Webhooks::Request#to_signable_string`, or independently verify that the shop domain in a delivered webhook matches a shop that is expected to be sending webhooks for the given topic/registration before invoking the handler. At minimum, document and enforce that `WebhookMetadata#shop` cannot be treated as authenticated unless the header is included in the HMAC computation.

### Proof of Concept
```ruby
# Attacker has a legitimate app installation on their own shop and captures
# a real webhook delivery: raw_body B, hmac-sha256 = HMAC(secret, B)

forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => captured_hmac_from_own_shop, # unchanged
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # swapped
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body_B, headers: forged_headers)

# Passes because HmacValidator only checks HMAC(secret, captured_body_B)
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker-controlled B)
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
