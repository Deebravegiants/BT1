This confirms the finding: `WebhookMetadata.shop` (a `const :shop, String`) is passed directly from `request.shop`, which reads the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header, while `Utils::HmacValidator.validate(request)` in `Registry.process` only verifies `request.to_signable_string`, which is `@raw_body` — the `shop` header is never part of the signed material. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but `#to_signable_string` — the value actually verified by `Utils::HmacValidator.validate` — is defined as only `@raw_body`. The `shop` (and `topic`, `webhook-id`, `api-version`) headers are never covered by the HMAC signature. Since a single app-wide `client_secret` (`Context.api_secret_key`) signs webhooks for every shop that installs the app, any merchant who legitimately installed the app can capture a real, validly-signed webhook delivered for their own store and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a different (victim) shop. The HMAC check still passes because it only validates the untouched body, so `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Finding Description
The identity binding that should hold is:
`verified_bytes(HMAC) == bytes_that_determine_tenant_shop`

In `Request`, `hmac` decodes the `hmac-sha256` header, and `to_signable_string` returns `@raw_body` only: [4](#0-3) 

`shop` is read straight from a header that is not part of that signable string: [5](#0-4) 

`Registry.process` validates only the HMAC of the request (i.e., the body) before trusting `request.shop` for tenant-scoped dispatch: [6](#0-5) 

Because `client_id`/`client_secret` (and hence the webhook signing secret) is shared across every shop that installs a given app, and the body-vs-header split is exactly the kind of "bytes verified vs bytes parsed" mismatch called out as in-scope, an attacker who is simply a legitimate, unprivileged merchant with their own shop can:
1. Install the target app on their own (attacker-controlled) shop.
2. Capture one of the genuine webhooks Shopify sends them (valid HMAC over the body, `shop-domain: attacker-shop.myshopify.com`).
3. Replay the exact same body/HMAC to the app's webhook endpoint, but substitute `shop-domain: victim-shop.myshopify.com` (and/or a different `topic`/`webhook-id`).
4. `HmacValidator.validate` still returns `true` because it never inspected the header, so `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`.

This breaks the tenant boundary that host apps rely on this gem's `Request`/`Registry` abstraction to enforce: the `shop` field handed to `WebhookHandler#handle` is supposed to identify the authenticated originator of the payload, but it is unauthenticated attacker input.

### Impact Explanation
This crosses the tenant boundary of the app: an attacker who only controls their own shop's webhook traffic can make the app process payloads under an arbitrary victim shop identity. Any app that keys persistence, side effects, or authorization decisions off `WebhookMetadata#shop` (which is exactly the field's documented purpose) can be tricked into associating attacker-supplied data/body with a victim tenant, corrupting that tenant's state or triggering shop-scoped actions (e.g., billing, inventory sync, order processing) using attacker-controlled body content labeled as the victim's. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires no privileged access, credentials, or leaked secrets — only that the attacker is able to install the app on their own shop (a normal, low-privilege action available to any Shopify merchant) and can send arbitrary HTTP requests to the app's public webhook endpoint. The relevant validation path is entirely inside this gem (`Utils::HmacValidator`, `Webhooks::Request`, `Webhooks::Registry`), not something a host app opts out of — apps are expected to call `Registry.process` as documented and trust the resulting `WebhookMetadata#shop`.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`/`api-version`) in the signable payload verified by the HMAC, e.g. by having `Request#to_signable_string` bind a canonical concatenation of those headers plus the raw body, and reject a request if the header-derived `shop` cannot be reconciled with a value cryptographically bound to the signature. At minimum, document that `shop-domain` is unauthenticated and must be revalidated by comparing against a store's registered offline session before use, and/or require callers to supply the expected shop out-of-band rather than trusting the header value returned by `Request#shop`.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and legitimately receives this webhook:
raw_body = '{"id":123,"note":"legit order for attacker shop"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker resends the identical body/HMAC but swaps the shop-domain header:
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(valid_hmac), # still valid: HMAC never covered shop header
  "shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
  "shopify-webhook-id" => "forged-id",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body untouched)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes attacker-controlled data as if it originated from the victim shop.
```

### Citations

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
