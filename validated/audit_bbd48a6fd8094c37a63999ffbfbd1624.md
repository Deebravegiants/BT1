Confirmed: the webhook HMAC signs only the raw body (`to_signable_string` returns `@raw_body` in `lib/shopify_api/webhooks/request.rb:36-38`), while `request.shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to that HMAC at all.### Title
Webhook `shop` Field Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` when dispatching to the host application's handler, so any actor who can produce one genuine HMAC-signed body for the app (e.g. by installing the app on their own store and capturing a real Shopify webhook) can replay that exact body against the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header and have it accepted as coming from a different, victim shop.

### Finding Description
The signable content used for HMAC verification is only the raw body: [1](#0-0) 

But `shop` (and `topic`, `api_version`, `webhook_id`) are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then forwards `request.shop` verbatim into `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The gem's own `HmacValidator.validate` confirms the signature check is scoped strictly to `to_signable_string` (the body), never the shop header: [4](#0-3) 

The documented contract explicitly (and incorrectly) tells integrators that `Registry.process` "will verify the request did indeed come from Shopify," implying the `shop` value handed to the handler is trustworthy: [5](#0-4) 

**Equality broken:** `shop_authenticated_by_hmac == shop_delivered_to_handler` does not hold. The HMAC authenticates `{app secret, raw_body}`; it says nothing about which shop the body pertains to. Because a single app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, any shop that has the app installed (an unprivileged actor, from the perspective of any other tenant) can capture a valid `(body, hmac)` pair from its own legitimate webhook traffic and replay it to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (or `shopify-shop-domain`) with a victim shop's domain. `HmacValidator.validate` will still pass because it only recomputes HMAC over the unchanged body, and `Registry.process` will invoke the app handler with `shop` set to the victim's domain.

### Impact Explanation
This breaks the shop-authentication boundary between tenants: an attacker who legitimately installed the app on their own store can trigger the app's webhook handler as if the event originated from a completely different merchant's store. Depending on how the host application's handler uses `data.shop` (a documented, expected field of `WebhookMetadata`), this enables cross-tenant actions — most notably for the gem's built-in mandatory GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`), where a replayed webhook with a forged `shop` could cause the app to redact/delete data belonging to a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category, since the identity binding that is supposed to scope a webhook event to one tenant is absent.

### Likelihood Explanation
Likelihood is high for any app author following the documented `Registry.process` usage exactly as shown in `docs/usage/webhooks.md`: no additional shop-consistency check is performed or suggested by the gem itself. An attacker only needs the ability to install the target app on a store they control (a normal, unprivileged action available to anyone with a Shopify dev/partner account) and a way to submit an HTTP POST to the app's public webhook route with modified headers — no `api_secret_key`, access token, or other privileged credential is required.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise independently confirm that the `shop` reported in headers matches a shop session/installation the app is currently tracking before invoking the handler. At minimum, update `Utils::VerifiableQuery#to_signable_string` for `Webhooks::Request` to incorporate the shop-domain header (canonicalized) into the signed payload, and document that consumers must cross-check `data.shop` against their own installation records rather than trusting the header outright.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (or is already a subscriber to a mandatory GDPR topic, which requires no explicit registration).
2. Shopify sends the attacker a legitimate webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: customers/redact
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"shop_id":123,"shop_domain":"attacker-shop.myshopify.com","customer":{...}}
   ```
   Attacker captures `(body, hmac)`.
3. Attacker replays the exact same request to the app's public webhook endpoint, only replacing the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
   (body and `x-shopify-hmac-sha256` unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the signature only over `@raw_body` — identical to step 2 — so validation succeeds: [6](#0-5) 
5. The app's handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, causing the app to act (e.g. redact data) on behalf of a shop the attacker never controlled: [7](#0-6)

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
