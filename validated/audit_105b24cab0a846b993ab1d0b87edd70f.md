### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` headers are trusted by `Registry.process` without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that the HMAC covers the raw request body. All of the identity-bearing fields the gem hands to the app's handler — `shop`, `topic`, `webhook_id`, and `api_version` — come from HTTP headers that are never included in the signed payload. An attacker who can obtain any one validly-signed `(raw_body, hmac)` pair (e.g., from a webhook legitimately delivered to their own installed shop) can replay that pair to the app's webhook endpoint while freely rewriting the `shop`-domain header to point at a victim shop, breaking the binding between "the HMAC that authenticates the sender" and "the shop the gem tells the app the data belongs to."

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, and for webhooks `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

None of `shop`, `topic`, `webhook_id`, or `api_version` — all parsed straight from HTTP headers in `initialize` — are part of the signed string: [2](#0-1) [3](#0-2) 

`Registry.process` performs exactly one check — HMAC over the body — and then unconditionally forwards the unauthenticated header values into `WebhookMetadata`, which is delivered to the app's handler as the trusted identity of the event: [4](#0-3) 

The documented handler contract explicitly tells integrators that `data.shop` is "The shop domain of the webhook" and shows it being used directly to key application logic (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), i.e., the gem's own documented API instructs the host app to trust `shop` as an authenticated tenant identifier: [5](#0-4) 

The equality that should hold — but doesn't — is:
`shop` (identity used by the app to select the tenant, sourced from `X-Shopify-Shop-Domain`) == `shop` (identity actually covered by the HMAC that Shopify computed over the request).

Before the attack: a legitimate webhook for shop A has header `shop=A` and `hmac = HMAC(secret, raw_body_A)`. Since `raw_body_A` doesn't encode `A` anywhere the app cannot rely on, an attacker who owns shop A (and thus legitimately receives real, validly-signed webhooks for their own store) can capture `(raw_body_A, hmac)`. After the attack: the attacker POSTs the exact same `raw_body_A`/`hmac` pair to the app's webhook endpoint with the header changed to `shop=victim-shop.myshopify.com` (and optionally a different `topic`/`webhook_id`). `HmacValidator.validate` still succeeds because it only checks `raw_body_A` against `hmac`, which are unchanged. `Registry.process` then dispatches to the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled data from their own real order/customer/etc.>)`.

### Impact Explanation
Any application built on this gem's webhook processing path can be made to attribute attacker-authored data to a victim merchant's tenant. Since almost all real-world usage of `data.shop` is to select the tenant's database/session/queue partition (as shown in the gem's own documentation example), this breaks the tenant boundary between shops using the same app — a cross-tenant data-injection primitive that requires no access token, no privileged account, and no interception, only that the attacker install the target app on any shop they control (a normal, unprivileged action for any Shopify merchant/attacker). This qualifies as Critical (cross-tenant access) under the stated impact criteria.

### Likelihood Explanation
High. Any user of the app can install it on their own store (a "free" merchant account), which entitles them to receive genuinely, validly-signed webhooks for that store. Capturing one such `(raw_body, hmac)` pair and replaying it with a forged `shop` header requires only basic HTTP tooling — no exploitation of a race condition or timing issue, and no reliance on host-app misuse beyond following the gem's documented `data.shop` contract.

### Recommendation
Include the authenticating headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before exposing them via `WebhookMetadata`. At minimum, document that `data.shop`/`data.topic`/etc. are unauthenticated and must not be used to select tenant context, and consider validating that the `shop` header matches a shop with an active installation/session known to the app before dispatch.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) so Shopify delivers a request to the app's webhook endpoint with a real `X-Shopify-Hmac-Sha256` computed over the real `raw_body`.
2. Intercept/log this request: capture `raw_body` and `X-Shopify-Hmac-Sha256` header value (attacker fully controls the resulting body content, e.g., by naming an order/customer field with attacker-chosen text).
3. Replay the exact same `raw_body` and `X-Shopify-Hmac-Sha256` to the same app endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally any `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — [6](#0-5)  — which passes because it only checks `raw_body` against the unchanged `hmac`.
5. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker content>, ...)` and (per the documented usage pattern) processes/stores it under the victim shop's tenant context.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-60)
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
