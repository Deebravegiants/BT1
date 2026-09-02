### Title
Webhook `shop` (and `topic`) identity is not bound to the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating only the HMAC of the raw request body. The `shop` (and `topic`) values that the handler subsequently trusts to identify the tenant are read from HTTP headers that are **not** part of the signed payload. Because the HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has installed the app, a legitimate webhook payload received for one shop remains validly signed even after its `shop-domain` header is swapped to name a different shop. This mirrors the reported bug class: a field that is acted upon (`shop`) is not covered by the integrity check (HMAC) that is used to authenticate the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors, however, come straight from HTTP headers, which are not included in that signable string: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received `hmac`, i.e. it only proves the body's integrity/authenticity, not the header values: [3](#0-2) 

`Registry.process` performs this body-only HMAC check and then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler, with no additional binding between the shop header and the signature: [4](#0-3) 

The documented integration pattern explicitly instructs the host application to construct the `Request` from raw headers and let the gem hand the resulting `shop` to the handler as the tenant identifier: [5](#0-4) 

Because `Context.api_secret_key` is the single app-wide secret (not shop-specific), any shop that has installed the app can receive a genuinely-signed webhook for its own tenant, then replay that exact body/HMAC pair to the app's webhook endpoint while altering only the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header. `Utils::HmacValidator.validate` still returns `true` (the body and HMAC are untouched), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop, even though the body content actually originated from — and was intended for — the attacker's own shop. This breaks the equality that should hold: `shop_bound_by_hmac == shop_used_by_handler`.

### Impact Explanation
This allows one tenant of a multi-tenant app to inject or spoof webhook events under another tenant's identity (cross-tenant confusion), because the library allows the host application to trust an unauthenticated `shop` header as if it were cryptographically tied to the validated payload. Per the report's impact categories this falls under cross-tenant access.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate installer of the target app (any merchant), capture one of their own genuine webhook deliveries, and resend it with a modified `shop-domain` header — no access to `client_secret`, tokens, or privileged accounts is needed, and no interception of TLS is required since the attacker crafts their own HTTP request to the app's public webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the HMAC-signed string, or otherwise cryptographically bind them to the payload before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document that host applications must independently verify the `shop` header against a known/expected shop for the webhook subscription (e.g. correlate against the webhook ID that was returned at registration time) rather than trusting it as an authenticated identity.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify sends a legitimately HMAC-signed webhook (e.g. `orders/create`) to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid_hmac_of_body>`, and some `raw_body`.
2. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` value to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body`: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, and any app logic keyed on `data.shop` (session/tenant lookup, per-shop data writes) now operates against the victim shop's identity using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
