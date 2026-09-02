I have enough evidence to finalize this finding.

### Title
Webhook `shop` Identity Not Bound by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then blindly trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers when constructing the `WebhookMetadata` passed to the app's handler. Because the HMAC signature never binds to the `shop` header, any unprivileged internet user who has captured one legitimately-signed `body`+`hmac` pair (trivially obtainable by installing/testing the app on their own free development store and receiving a real webhook) can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The gem will report the HMAC as valid and hand the handler data attributed to a victim shop chosen entirely by the attacker.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for webhooks this string is defined as: [1](#0-0) 

i.e., only the raw JSON body. The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC and, if it matches, immediately forwards `request.shop` (an unauthenticated header value) to the app's handler as the tenant identity for the event: [4](#0-3) 

`WebhookMetadata#shop` is a plain, unauthenticated `String` field consumed by the handler interface for all tenant-scoped business logic (e.g. `shop/redact`, `customers/redact`, `orders/*`, app uninstall handling): [5](#0-4) 

This is the same identity-binding class as the referenced report: a field that is *acted on* (`shop`, used to route/attribute the webhook event to a tenant) is not *covered by the HMAC* that authenticates the request. The equality the code implicitly assumes is:

`shop authenticated by HMAC == shop trusted by the handler for tenant-scoped action`

but in reality:

`shop authenticated by HMAC (⊆ body only) ≠ shop header value used by handler.handle`

An attacker who legitimately receives one webhook for *their own* shop (any developer can freely create a shop and install their own or a target's public app to receive a real webhook + valid HMAC) can then POST that identical `raw_body` with its valid HMAC to the app's public webhook endpoint, overriding only the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to name a different, victim shop. `Utils::HmacValidator.validate` will pass because the secret and body are unchanged, and `Registry.process` will invoke the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing — a Critical-class cross-tenant access issue. Depending on how the host app implements its handlers (which is the expected, documented usage of this exact API), an attacker can:
- Trigger `shop/redact` / `customers/redact` / `customers/data_request` (GDPR) logic against an arbitrary victim shop, causing wrongful data deletion or disclosure decisions tied to the wrong tenant.
- Spoof `app/uninstalled` for a victim shop, corrupting the host app's session/subscription state for that tenant.
- Inject falsified order/product/customer event data attributed to a victim shop's tenant record, corrupting downstream tenant-scoped data stores that key off `WebhookMetadata#shop`.

All of this is achievable by an unprivileged internet user with no access token, no `api_secret_key`, and no privileged account — only a single legitimately-received webhook body/HMAC pair from any shop (including their own) and the ability to send an HTTP POST to the app's public webhook URL.

### Likelihood Explanation
High. Webhook endpoints are public URLs by design; capturing one genuine `(body, hmac)` pair requires nothing more than installing the app (or a similar sibling app using this gem) on a free development store and observing one webhook delivery. Replaying it with a forged `shop-domain` header requires only a normal HTTP client. `HmacValidator.validate` and `Webhooks::Request` perform no cross-check that the `shop` header matches any tenant-specific secret or that the body content actually pertains to that shop.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) values into the signable payload that the HMAC covers, or at minimum verify that the shop asserted in the header matches a shop-specific secret/session record before invoking the handler, rather than trusting the header purely on the strength of a body-only HMAC. Concretely, extend `Webhooks::Request#to_signable_string` (or add a parallel verification step in `Registry.process`) to incorporate the `shop-domain` header into the value verified by `Utils::HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target (or a functionally identical) Shopify app on their own store `attacker-shop.myshopify.com` and captures a genuine webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for the app's shared `client_secret`).
2. Attacker sends:
```
POST /webhooks HTTP/1.1
x-shopify-topic: shop/redact
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim-shop.myshopify.com
x-shopify-webhook-id: <any>
x-shopify-api-version: 2024-01

B
```
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only re-derives the HMAC from `B` (`to_signable_string`) — identical to what was captured.
5. The registered handler executes `handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "shop/redact", body: JSON.parse(B), ...))`, causing the host app to perform tenant-scoped action against `victim-shop.myshopify.com` on the attacker's behalf, despite the attacker having no relationship with that shop.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
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
    end
```
