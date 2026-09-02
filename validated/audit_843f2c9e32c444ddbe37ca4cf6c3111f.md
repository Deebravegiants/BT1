### Title
Webhook Shop Domain Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC computed over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` header as the tenant identity that gets handed to the application's webhook handler. Because the shop domain is never part of the signed payload, an attacker who owns a legitimate, signed webhook body (from their own app installation) can replay it with a forged shop-domain header and have it accepted as belonging to a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The `shop` (and `topic`, `webhook_id`, `api_version`) values are pulled independently from HTTP headers that are not part of that signable string: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, and — once that passes — unconditionally trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` computes the digest exclusively from `verifiable_query.to_signable_string` (the body), never incorporating the shop header: [4](#0-3) 

The gem's own documentation instructs developers to treat `data.shop` from the handler as the authenticated shop for the webhook and to key application logic (e.g., job dispatch) off of it, and states that `Registry.process` "will verify the request did indeed come from Shopify": [5](#0-4) [6](#0-5) 

This breaks the identity binding: `shop that produced the signed body` ≠ `shop attributed to the data by the gem`. An unprivileged attacker can install the target app on their own store (a normal, unprivileged action requiring no secrets), capture a genuinely Shopify-signed webhook body+HMAC pair delivered to their own endpoint, and then POST that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it never inspected the header, and `Registry.process` dispatches the attacker-controlled body to the handler labeled as belonging to the victim shop.

### Impact Explanation
This allows cross-tenant data injection into a merchant's application state: the receiving app processes attacker-supplied webhook payloads (order/product/customer data, GDPR-style redact events, etc.) as if they originated from the victim shop, without ever needing the app's `client_secret`, an access token, or any privileged credential. This matches the "Critical: cross-tenant access" category because a genuinely-authenticated (HMAC-valid) request can be misattributed to any shop of the attacker's choosing.

### Likelihood Explanation
Any developer/attacker can freely create a development or trial store, install the target app themselves (no special privilege needed), and receive genuinely signed webhooks addressed to their own endpoint. Forging the `x-shopify-shop-domain` header on replay is trivial once the legitimate body+HMAC pair is captured, so likelihood is high for any app that relies on the documented `data.shop` value for tenant-sensitive logic (as the gem's own docs recommend).

### Recommendation
Bind the shop domain (and ideally topic/webhook-id) into the value verified by the HMAC, or require the caller to separately confirm that `request.shop` corresponds to a shop with a currently valid, previously-established session/access token before trusting it as a tenant key. At minimum, update `to_signable_string` semantics/documentation so consuming apps are not told that `Registry.process` fully "verifies the request did indeed come from Shopify" for the shop attribution, and clarify that `data.shop` must be cross-checked against known installed shops before being used for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) that Shopify signs and delivers to the app's registered callback URL, with headers including `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker intercepts/logs this raw body and its HMAC (trivial since it is delivered to an endpoint they control/observe as the app owner for their own store).
3. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in [4](#0-3)  succeeds because it only checks the body-derived signature.
5. `Registry.process` in [3](#0-2)  builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches attacker-controlled body content to the app's handler as if it were data belonging to the victim shop.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
