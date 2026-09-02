This confirms the analysis is complete. The webhook HMAC signature in `ShopifyAPI::Webhooks::Request` covers only the raw request body, while the `shop` (and `topic`) fields consumed downstream are taken from unauthenticated HTTP headers.### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content solely from the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` values consumed by `ShopifyAPI::Webhooks::Registry.process` and handed to app handlers via `WebhookMetadata` are read directly from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.). None of these header values are included in the HMAC-signed content, so the binding "the shop that the handler is told the event came from" == "the shop whose secret actually signed this payload" is never enforced.

### Finding Description
- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `shop`, `topic`, `api_version`, `webhook_id` are all pulled from headers, not from the signed body: [2](#0-1) 
- `HmacValidator.validate` only checks that `hmac` matches `compute_signature(to_signable_string, secret)` — i.e., it authenticates the body bytes, not the headers: [3](#0-2) 
- `Registry.process` trusts `request.shop`/`request.topic` (headers) once the body-only HMAC passes, and forwards them into `WebhookMetadata` for the app's handler to act on: [4](#0-3) 
- `WebhookMetadata.shop` is a plain, unauthenticated `String` field consumed by host-app handlers as the tenant identity for the event: [5](#0-4) 

Because the HMAC only binds the body bytes, any attacker who can obtain one genuine `(raw_body, hmac)` pair signed with the app's `client_secret` — trivially available to them by installing the app on their own (attacker-controlled) shop and capturing a real webhook delivery — can replay that exact body+hmac to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will invoke the registered handler with `WebhookMetadata.shop` set to the spoofed victim domain. The broken identity binding is: `request.shop` (attacker-controlled header) == the shop that actually authorized/produced the signed payload (attacker's own shop) — these are never required to match.

### Impact Explanation
This is a cross-tenant identity confusion: an app handler that keys any side effect (data lookup, GraphQL mutation, cache invalidation, mandatory GDPR webhook processing, etc.) off `WebhookMetadata.shop` can be tricked into acting against/for the wrong merchant's tenant using an attacker-supplied body that was never actually produced by that merchant. Depending on the handler logic this can lead to cross-tenant data exposure or mutation performed under the wrong shop's identity, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Requires only an unprivileged internet user who can install the app on any shop (including their own free/dev store) to obtain one legitimately signed webhook body+hmac pair, then send a forged HTTP request with a different `shopify-shop-domain` header value and the same body/hmac to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — the attacker only needs the app's public webhook URL and a legitimate delivery to replay against.

### Recommendation
Bind the shop (and ideally topic/webhook id) to the HMAC-verified content, e.g., by requiring apps to independently correlate the header-derived shop against data embedded in the (signed) body, or by extending the signable string to include the header values that downstream code trusts for tenant identity, so a body signed for shop A cannot be replayed while claiming to originate from shop B.

### Proof of Concept
1. Install the target app on an attacker-owned/controlled shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g., `orders/create`) and capture the raw POST: body `B`, and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's real `client_secret`), along with `x-shopify-shop-domain: attacker.myshopify.com`.
3. Replay this exact request to the same app webhook endpoint, but replace only the `x-shopify-shop-domain` header with `victim.myshopify.com`.
4. `HmacValidator.validate` computes `compute_signature(B, secret)` and compares to `H` — passes, since `B` and `H` are unchanged (see [3](#0-2) ).
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` (see [6](#0-5) ), causing the app to process attacker-supplied data as if it originated from the victim shop.

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
