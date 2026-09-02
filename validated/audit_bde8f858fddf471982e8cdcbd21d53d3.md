### Title
Webhook shop/topic identity spoofing due to HMAC covering only the raw body - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a request as fully authenticated ("verify the request did indeed come from Shopify") once the HMAC check passes, and then dispatches the handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken straight from HTTP headers. However, the HMAC signature is computed and verified over the raw body only, never over these headers, so an attacker who has captured one legitimately-signed webhook delivery (e.g. one sent to their own store) can replay the same body+HMAC pair with forged `x-shopify-shop-domain` / `x-shopify-topic` headers and have it accepted as coming from a different shop or topic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `to_signable_string`: [2](#0-1) 

`Registry.process` uses this single check as the *entire* authenticity gate, then blindly trusts `request.topic` to select the handler and `request.shop` to build the `WebhookMetadata` passed to it: [3](#0-2) 

`request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all read directly from attacker-controllable headers with no cryptographic binding to the body that was actually signed: [4](#0-3) 

The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify and then call the specified handler," implying the full `WebhookMetadata` (including `shop`) is trustworthy: [5](#0-4) 

This is the same class of bug as the reported analog: one piece of data (`raw_body`) is verified, but a *different* piece of data (`shop`, `topic`, headers) is what the code actually acts on and hands to the tenant-scoped handler — an identity binding is asserted (`verified body == acted-upon shop/topic`) that the code does not enforce.

### Impact Explanation
Because `shop` is not bound to the signature, a party who legitimately receives one webhook for their own store (a normal, unprivileged action — installing the app and receiving any webhook) can capture that body+HMAC pair and resend it to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop (and/or a forged `x-shopify-topic`). The HMAC check still passes because it only ever validated the body bytes. Downstream, the host app — following this gem's documented guarantee that `process` verifies the request "did indeed come from Shopify" — will process attacker-supplied webhook content under a different tenant's identity, causing cross-tenant data corruption/injection (e.g. fake `orders/create`, `customers/redact`, or other topic events falsely attributed to another shop). This crosses a tenant boundary using only credentials the attacker legitimately possesses for their own store, meeting the "cross-tenant access" impact bar.

### Likelihood Explanation
The attacker only needs a legitimate app installation (any merchant/developer store) to receive at least one real webhook delivery, then can freely replay/modify headers when POSTing to the app's known public webhook endpoint. No `api_secret_key`, access token, or privileged account is required — only the ability to observe traffic destined for their own server, which is trivial for a store owner. The attack requires no cryptographic break, only reordering which fields are treated as authenticated.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed payload, or otherwise cryptographically bind them to the verified body, so replaying a body under different header values fails validation. At minimum, update `Registry.process`/documentation to clarify that only the payload body is authenticated and that host applications must independently correlate `data.shop` against a known/installed shop (e.g. from their own session store) before trusting it.

### Proof of Concept
1. As the operator of `attacker-shop.myshopify.com`, install the app and let Shopify deliver a real webhook, e.g.:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid HMAC of BODY>
x-shopify-shop-domain: attacker-shop.myshopify.com
Body: BODY
```
2. Capture `BODY` and the valid `x-shopify-hmac-sha256` value.
3. Replay the same request directly against the app's public webhook endpoint, changing only the shop/topic headers:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <same valid HMAC of BODY>
x-shopify-shop-domain: victim-shop.myshopify.com
Body: BODY
```
4. `Utils::HmacValidator.validate` returns `true` (body unchanged, signature matches), and `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: parsed BODY, ...)`, causing the app to process attacker-controlled data under `victim-shop`'s tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
