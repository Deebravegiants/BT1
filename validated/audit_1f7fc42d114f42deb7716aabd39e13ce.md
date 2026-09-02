This is a genuine finding: the `shop` field consumed by the app's webhook handler is taken from an HTTP header that the HMAC never covers.

### Title
Webhook `shop` header is not covered by HMAC verification, enabling cross-tenant impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then hands the host application a `WebhookMetadata` struct whose `shop` attribute comes from an HTTP header that was never part of the signed payload. Any party that can obtain one genuinely-signed webhook body/HMAC pair for the shared app secret can replay that body with a different `shopify-shop-domain` header and have the host app's handler attribute the event to an arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is disjoint from the signed bytes: [2](#0-1) .

`Registry.process` validates only the HMAC over `to_signable_string` (i.e., the body) via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` when building the `WebhookMetadata` passed to the host's handler: [3](#0-2)  and [4](#0-3) .

`HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`, i.e., the body — it never incorporates the shop domain: [5](#0-4) .

This breaks the identity binding `hmac_signed_bytes == raw_body` while the application-facing identity used by every handler is `data.shop == header["shopify-shop-domain"]` — a value that was never part of what the HMAC signs. Since a single app has one `client_secret` shared across every installed shop, anyone who is themselves a legitimate merchant of the app (or otherwise obtains one valid `(raw_body, hmac)` pair, e.g. by having their own shop trigger a webhook) can capture that pair and resend it to the app's webhook endpoint with the `shopify-shop-domain` header swapped to a victim shop's domain. `Registry.process` will accept it as valid (the HMAC matches the unmodified body) and dispatch `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` to the handler, exactly as documented for legitimate use: [6](#0-5) .

### Impact Explanation
This is a cross-tenant identity-boundary break inherent to the gem's own webhook verification API: the value host applications are told to trust for tenant attribution (`data.shop`) is not covered by the cryptographic check the gem performs, and no alternate binding (e.g., HMAC-including-shop, or per-shop signing) is offered. An attacker controlling one tenant's webhook traffic can inject events — with attacker-controlled `body` content up to the topic's schema — attributed to a different, victim shop into the host app's business logic (e.g., `orders/create`, `app/uninstalled`, `shop/redact`), which most apps use to key data lookups/writes by `shop`. This matches "cross-tenant access" impact.

### Likelihood Explanation
Any developer of the app already possesses at least one legitimate shop connection needed to receive real signed webhook traffic (this is the ordinary state of any multi-tenant Shopify app with more than one installed merchant, including possibly the attacker's own test store). No `api_secret_key` or access token is required to mount the attack: only a previously-observed valid `(body, hmac)` pair and the ability to POST to the app's public webhook endpoint with a forged `shop-domain` header, both attacker-controlled.

### Recommendation
Bind the shop identity into the signed material, or independently re-verify it: either (a) include the shop domain in the HMAC-signable string (`to_signable_string`) so a mismatched header invalidates the signature, or (b) require/encourage host apps to compare `request.shop` against the shop domain that was used during that webhook's registration, and document this requirement prominently, rather than presenting `data.shop` as trustworthy after `Utils::HmacValidator.validate` succeeds.

### Proof of Concept
1. As a legitimate merchant "attacker-shop.myshopify.com" on the target app, trigger any subscribed webhook topic (e.g. `orders/create`) and capture the raw POST: `raw_body` plus `x-shopify-hmac-sha256` header sent by Shopify (signed with the app's shared `client_secret`).
2. Resend that exact captured request to the app's webhook route, only replacing `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) , which recomputes the HMAC over `raw_body` only and matches the unmodified, still-valid signature.
4. `request.shop` returns `"victim-shop.myshopify.com"` [2](#0-1) , and the handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to process attacker-supplied data under the victim tenant's identity.

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
