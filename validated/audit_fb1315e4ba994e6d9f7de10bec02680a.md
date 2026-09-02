## Analysis: Webhook shop-domain not bound to HMAC signature

The reported bug class is "a field is used by the application logic without being covered by the integrity check used to authenticate the request." The closest analog in this gem's own code (excluding generated REST resources) is in the webhook signature verification path.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, and the HMAC validator computes/verifies the signature exclusively over that body: [1](#0-0) 

The `shop` accessor, however, is read straight from an attacker-controllable HTTP header (`x-shopify-shop-domain` / `shopify-shop-domain`) and is never included in the signed material: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` as the tenant identifier and hands it to the application's webhook handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm this: they only ever hash `verifiable_query.to_signable_string`, never the shop header: [4](#0-3) 

### The broken equality

The binding the gem implicitly claims to provide is:

`shop delivered in WebhookMetadata == shop the HMAC-signed body actually originated from`

But since the signature only covers `raw_body`, this equality is never checked — the `shop` header rides along unauthenticated. An unprivileged internet user who can obtain one valid `(raw_body, hmac)` pair for their own shop (trivial: install the app on an attacker-owned dev shop and trigger any webhook) can resend the exact same body/HMAC pair while substituting a victim's `shop-domain` header value. `HmacValidator.validate` still succeeds because it never looked at the header, and `Registry.process` passes the attacker-forged shop identity straight to `WebhookMetadata`/the handler as if the data originated from the victim's shop.

This is documented as the intended integration pattern — the sample controller in the docs forwards `request.headers.to_h` (including the shop header) directly into `Webhooks::Request`, and the handler is expected to trust `data.shop`: [5](#0-4) 

### Assessment against scope rules

This crosses a real tenant-authentication boundary (the `shop` value used to key merchant data) without requiring any credential, and it does not depend on the host app "ignoring documented API" — using `request.shop` from a verified `Webhooks::Request` is exactly the documented, intended usage. It is a legitimate analog of "a field acted on but not covered by the HMAC."

### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop` (and `topic`/`api_version`/`webhook_id`) are read from unauthenticated HTTP headers. `Utils::HmacValidator` verifies the HMAC solely against the body, so `Webhooks::Registry.process` accepts and forwards a `shop` value that was never bound to the signature.

### Finding Description
`Registry.process` gates webhook processing purely on `Utils::HmacValidator.validate(request)`, which internally hashes `request.to_signable_string` (the raw body only) and compares it to the provided HMAC. `request.shop` is derived independently from the `x-shopify-shop-domain`/`shopify-shop-domain` header and is never part of that computation. Consequently, given any valid `(body, hmac)` pair — obtainable by an attacker triggering a webhook on their own installed/dev shop — the attacker can replay the identical body and HMAC to the app's public webhook endpoint while swapping the `shop-domain` header to point at a victim shop. The signature check still passes, and the forged `shop` value flows unchecked into `WebhookMetadata` given to the app's handler.

### Impact Explanation
This breaks the tenant-identity binding `signed_shop == acting_shop` that the HMAC is meant to guarantee, allowing a low-privilege attacker (with access to only their own shop's webhooks) to inject attacker-controlled webhook payloads that the host application will process as if they belong to a different merchant/tenant — a cross-tenant data-integrity/confidentiality issue in any app that keys per-shop state or side effects off `WebhookMetadata#shop`.

### Likelihood Explanation
High reachability: any developer following the documented pattern (`Registry.process` fed by raw headers/body, per `docs/usage/webhooks.md`) is exposed. The only prerequisite is that the attacker control one shop that has the app installed (a standard, unprivileged capability for any Shopify Partner/dev store), then forge headers on a replayed request to the app's own public webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) inside the signed material, or otherwise cryptographically bind the header values to the payload before trusting them — e.g., verify `shop` against a session/store already known to the app for that specific installation, rather than trusting the header value that arrives alongside a body-only HMAC.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering any webhook so Shopify sends a legitimately signed `(raw_body, x-shopify-hmac-sha256)` pair to the app's endpoint.
2. Attacker captures that request, then replays it to the same endpoint, changing only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `Webhooks::Request.new` builds `shop` from the forged header; `HmacValidator.validate` recomputes the HMAC over `raw_body` only, matches, and returns `true` (see `hmac_validator.rb` lines 26-31 and `request.rb` lines 35-38).
4. `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, even though the payload never originated from that shop.

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
