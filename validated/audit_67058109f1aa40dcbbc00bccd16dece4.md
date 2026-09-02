### Title
Webhook `shop` (and other Shopify headers) are not covered by the HMAC signature, allowing cross-tenant shop-domain spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` by defining `to_signable_string` to return only the raw HTTP body, while `shop` (and `topic`, `api_version`, `webhook_id`) are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body only and then forwards `request.shop` to the handler as the trusted tenant identifier, so the shop identity is never bound to the signature that supposedly authenticates the webhook.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

and `Request#shop` is derived purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header, independent of the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies the received HMAC by recomputing over `verifiable_query.to_signable_string` only: [3](#0-2) 

`Registry.process` performs this HMAC check and, on success, immediately trusts `request.shop` as the authoritative tenant identifier passed to the app's handler: [4](#0-3) 

The equality that should hold is: **shop bound in the cryptographic signature == shop delivered to the handler**. Instead, the gem enforces only: **body bound in the signature == body delivered to the handler**, while `shop` (the identity-binding field host apps are documented to rely on) passes through unauthenticated. Any HTTP body/HMAC pair the attacker can legitimately obtain for shop A can be replayed with the `shop-domain` header rewritten to shop B, and `Registry.process` will still accept it and deliver `WebhookMetadata.new(shop: "shop-B", body: <shop-A's body>, ...)` to the handler.

### Impact Explanation
This breaks the shop/tenant identity binding that host applications rely on for HMAC-verified webhooks — the documented processing flow in this library is exactly `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body:, headers:))`, and the resulting `WebhookMetadata#shop` is the value host apps are expected to trust to select/act on the correct merchant's tenant data. An attacker who can obtain any one valid `(raw_body, hmac)` pair (trivially available since anyone can install the target app on their own free development store and capture the webhook Shopify sends them) can replay that exact body/HMAC with an arbitrary victim `shop-domain` header. The forged request passes `Utils::HmacValidator.validate` and is routed to the handler tagged with the victim shop, enabling cross-tenant webhook injection/spoofing against any app built on this gem's documented webhook API.

### Likelihood Explanation
No credentials, access token, or `api_secret_key` are required — capturing a single valid webhook delivery for a shop the attacker controls (by installing the target app in their own store) is sufficient, and the header rewrite is trivial for anyone able to reach the app's public webhook endpoint.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, e.g., include the shop-domain header (and other identity-relevant headers) in `to_signable_string`, or independently verify that the shop-domain header matches an expected/registered value before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers/receives any webhook (e.g. `orders/create`), capturing the raw body and its valid `x-shopify-hmac-sha256` value from the real Shopify delivery.
2. Attacker sends a POST to the app's webhook endpoint with the exact same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only covers `raw_body`, unaffected by the header change (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker's original payload>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to process attacker-controlled webhook data under the victim shop's tenant context.

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
