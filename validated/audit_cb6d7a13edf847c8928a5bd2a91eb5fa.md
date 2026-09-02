### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only HMAC-verifies the raw request body, while the shop identity used to route and label the processed data is taken from an unauthenticated header that is never covered by the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates only the body/HMAC pair via `Utils::HmacValidator.validate`, and then unconditionally forwards `request.shop` (plus `topic`, `api_version`, `webhook_id`, all likewise unauthenticated headers) to the app's handler as trusted `WebhookMetadata`: [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the signature purely from `verifiable_query.to_signable_string`, i.e. the raw body only: [4](#0-3) 

The identity binding that should hold is: `HMAC(secret, bytes_verified) == HMAC(secret, bytes_acted_on)`, where `bytes_acted_on` includes the `shop` value used to attribute/route the webhook. Here `bytes_verified = raw_body` while `bytes_acted_on = raw_body ∪ {shop, topic, webhook_id, api_version}` — the equality is broken because the extra fields are parsed and acted upon but never covered by the HMAC.

The gem's own documentation states this call "will verify the request did indeed come from Shopify," implying the whole request (including shop attribution) is authenticated: [5](#0-4) 

In reality, `api_secret_key` is shared across all shops installed on a given app (it is not a per-shop secret — see `HmacValidator.validate` using `Context.api_secret_key`/`Context.old_api_secret_key` globally). Any shop that has installed the app can trigger a real Shopify event in its own store, obtaining a legitimate `(raw_body, hmac)` pair signed with the app's shared secret. That attacker-controlled shop can then replay the same body/HMAC to the app's public webhook endpoint while spoofing the `x-shopify-shop-domain` header to name a victim shop. `Registry.process` will accept it as valid (the HMAC only checks the body) and the handler will receive `WebhookMetadata` attributing the attacker's payload to the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem's webhook API is documented to enforce: any app-installed shop can forge webhook events "on behalf of" another shop, causing the host application to process attacker-supplied data (order/product/customer content, `body`) under a victim shop's identity. Depending on how the host app uses `data.shop` (e.g., to locate the merchant record, apply defaults, or make follow-up authenticated API calls with that shop's stored session/access token), this can lead to cross-tenant data corruption, impersonation, or triggering privileged actions against the wrong merchant — a cross-tenant access issue.

### Likelihood Explanation
Requires only that the attacker control (or have installed) any single shop on the target app — no `api_secret_key`, access token, or privileged account is needed, and no TLS interception is required. The attacker simply performs an action in their own store to elicit a real Shopify webhook (valid HMAC over that body) and replays it to the app's public callback endpoint with a modified shop header. This is directly reachable via the gem's documented `Registry.process` entry point.

### Recommendation
Bind the shop (and ideally topic/webhook_id) identity into the value that is actually verified, e.g., require the caller to pass the expected `shop` for the route/tenant context being processed and assert it matches an independently-trusted source (such as the shop associated with a per-shop webhook secret, or a shop already known to be installed via session lookup) rather than trusting the unauthenticated header value returned by `Request#shop`. At minimum, document explicitly that `shop`/`topic`/`webhook_id`/`api_version` are NOT covered by the HMAC and must be independently corroborated by the host app (e.g., cross-checked against the shop that owns the stored session) before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and captures a legitimate webhook request Shopify sends for that shop, e.g. body `{"id":1,...}` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` from the spoofed header (`lib/shopify_api/webhooks/request.rb:20-23`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` and succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process attacker data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L123-135)
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
