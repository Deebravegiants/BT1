## Analysis Result

### Title
Webhook Shop-Domain Spoofing via HMAC Signature That Only Covers the Request Body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, then immediately trusts `request.shop` — a value read straight from the `x-shopify-shop-domain` HTTP header — to build the `WebhookMetadata` passed to the app's business-logic handler. However, the HMAC signature computed by `ShopifyAPI::Webhooks::Request#to_signable_string` covers only the raw request body; none of the identifying headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) are part of the signed content. Since Shopify webhook signing uses a single shared secret (`Context.api_secret_key`, the app's `client_secret`) across every shop that installs the app, any unprivileged merchant who installs the app on their own store can capture a genuinely-signed webhook delivery and replay its body+HMAC to the app's webhook endpoint while swapping only the `x-shopify-shop-domain` header to a victim shop. The signature check still passes because the header was never covered by it, and the gem hands the forged shop identity straight to the handler.

### Finding Description
The identity binding that should hold is:
`shop attributed to the webhook by the handler == shop that Shopify actually authenticated the payload for`

`HmacValidator.validate` verifies only:
```ruby
computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
``` [1](#0-0) 

and for webhooks, `to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

Meanwhile `shop` is parsed from a header that is never mixed into the signed string:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

`Registry.process` validates the HMAC and then forwards the unverified `shop` value directly to the handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

Because the same `api_secret_key` is used to sign webhooks for *every* shop that has installed the app (it is the app's `client_secret`, not a per-shop secret), a valid `hmac`/`raw_body` pair legitimately obtained by one shop (via that shop's own installation) remains valid regardless of which `shop-domain` header accompanies it. An attacker who owns/installs the app on their own store can:
1. Receive a real webhook delivery (e.g., `orders/create`) with a valid `x-shopify-hmac-sha256` for the body.
2. Replay the identical body and HMAC to the app's webhook endpoint, replacing only `x-shopify-shop-domain` with a victim shop's domain.
3. `HmacValidator.validate` passes (body unchanged), and `WebhookMetadata.shop` is now the attacker-chosen victim domain.

The host application's handler (per the documented usage pattern in `docs/usage/webhooks.md`) trusts `data.shop` as the authenticated tenant identity, exactly as instructed by this gem's own documentation:
```ruby
def handle(data:)
  perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
end
``` [5](#0-4) 

This is a within-gem root cause (not a host-app misuse): the gem's own `Request`/`Registry` API supplies `shop` as if it were authenticated by the HMAC check it just performed, when it was not.

### Impact Explanation
This breaks the tenant isolation guarantee the HMAC check is meant to provide. An attacker can inject or spoof webhook events (order data, `app/uninstalled`, `shop/redact`, `customers/data_request`, etc.) attributed to any other shop using the same app, causing the app to act on another tenant's data/identity without ever compromising that tenant's credentials — a cross-tenant access issue (Critical per the rubric).

### Likelihood Explanation
Likelihood is high for any developer relying strictly on the gem's provided `Request`/`Registry` API as documented: no special access is needed beyond installing the target public app on an attacker-controlled shop (a normal, unprivileged action any merchant can perform), and capturing/replaying one's own legitimately-received webhook HTTP request with a modified header is trivial.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed content that binds the HMAC, or otherwise cryptographically bind the `shop-domain` header to the verified payload before trusting `request.shop`. At minimum, `Registry.process` should independently validate that `request.shop` corresponds to a shop with an active, registered webhook subscription for `request.webhook_id`/`topic` before invoking the handler, rather than trusting the header purely on the strength of a body-only HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers for a webhook topic (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC over raw body, signed with the app's shared client_secret>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>
   {...order json...}
   ```
3. Attacker replays the exact same request to the same endpoint, only changing:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Registry.process` computes `HmacValidator.validate(request)` using only `@raw_body` — unchanged — so the check passes.
5. `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` is passed to the app handler, which processes the payload as if it were authentic data for `victim-shop.myshopify.com`, per the exact usage pattern shown in `docs/usage/webhooks.md`.

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
