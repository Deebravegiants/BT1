### Title
Webhook HMAC verifies only the raw body, not the `shop`, `topic`, or `webhook_id` header values, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, while the `shop`, `topic`, and `webhook_id` values used afterwards come from unauthenticated HTTP headers that are never included in the signed bytes.

### Finding Description
`Utils::HmacValidator.validate` computes/compares the signature against `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from HTTP headers with no cryptographic binding to the HMAC at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` and `request.topic` to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Because the HMAC only covers `raw_body` bytes, this equality is never actually enforced — `shop` (and `topic`/`webhook_id`) can be swapped to any value by whoever controls the HTTP headers of the request reaching the app's webhook endpoint, without invalidating the HMAC, since the signature is unaffected by header content.

### Impact Explanation
Any attacker who can obtain one genuinely-signed webhook body (e.g., a webhook Shopify sends to their own store, which they fully control) can replay that exact body to a victim app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a different (victim) shop domain, and/or substituting `X-Shopify-Topic`. The HMAC check in `Registry.process` still passes because it only checks `raw_body`, so the forged `shop`/`topic` values flow unauthenticated into `WebhookMetadata` and into the app's webhook handler. Any host application logic that uses `WebhookMetadata#shop` to look up a stored session/access token or make shop-scoped decisions can be tricked into acting on data attributed to the wrong shop — a cross-tenant confusion condition rooted entirely in this gem's `Request`/`Registry` verification logic.

### Likelihood Explanation
Likelihood is high for the specific header-substitution mechanics (no secret material needed to modify headers), but it does require the attacker to first possess a validly HMAC-signed body — the easiest way is for the attacker to control their own myshopify.com store and forward the real webhook payloads and HMAC it receives (whose HMAC is generated with the app's own secret and thus still valid for header-swapped requests) to the target app's public webhook endpoint with modified `shop`/`topic` headers.

### Recommendation
Include `shop`, `topic`, and any other identity-relevant header the handler relies on in the signable bytes used to compute/verify the HMAC (Shopify's actual webhook signature is computed over the raw body only by design, so the gem instead needs to independently verify that these header-derived fields correspond to the endpoint/registration the handler expects, e.g., by validating `shop` against an active session/shop registered for that topic before dispatching to the handler, or by explicitly documenting that `shop`/`topic` are unauthenticated and must be re-validated by the host application before use).

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and receives a legitimate webhook from Shopify for topic `orders/create` with body `{"id":1,...}` and a valid `X-Shopify-Hmac-Sha256` header computed over that body with the app's `client_secret`.
2. Attacker resends the identical body and HMAC header to the victim app's public webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `Registry.process` passes because it only checks `raw_body`/HMAC, per [4](#0-3) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload never originated from Shopify for that shop, per [5](#0-4) .

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
