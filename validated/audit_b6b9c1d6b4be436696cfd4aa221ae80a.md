### Title
Webhook shop-domain (and topic) identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies nothing but the body bytes. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from unauthenticated HTTP headers and handed to the registered handler as trusted identity, without ever being part of the signed payload.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are the two methods used by `Utils::HmacValidator.validate`: [1](#0-0) 

`to_signable_string` returns `@raw_body` only — it does not include `topic`, `shop`, `webhook_id`, or `api_version`. Those accessors instead read directly from the caller-supplied `headers` hash via `shopify_header`: [2](#0-1) 

`Registry.process` validates only the body/HMAC pair, then immediately trusts `request.shop` and `request.topic` (parsed from headers) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`shop used to authorize/attribute the webhook == shop covered by the verified HMAC`

Because the signable string is `raw_body` alone, this equality does not hold — `shop`/`topic`/`webhook_id`/`api_version` are bytes that are *parsed* but never *verified*. Any request whose `raw_body` + `hmac` pair is valid for the configured `api_secret_key` will pass `HmacValidator.validate` regardless of what `shop-domain`/`topic` headers say. An attacker who obtains one legitimate `(raw_body, hmac)` pair — e.g. by installing the app on their own store and having Shopify deliver a real webhook to the app's public endpoint — can replay that exact body+HMAC to the same public endpoint while swapping the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a victim shop. `Registry.process` will accept it as valid and hand the host application a `WebhookMetadata` claiming the event belongs to the victim shop, since the shop field is never covered by the signature.

### Impact Explanation
This breaks the shop-identity binding at the point where the host application decides which tenant's data/session the webhook payload applies to (e.g., session lookup, data deletion/redaction, order/inventory updates keyed by `shop`). A single valid HMAC obtained from the attacker's own tenant can be replayed to make the app believe the event originated from an arbitrary other shop, i.e. cross-tenant confusion/access — matching the High-impact class "cross-tenant access."

### Likelihood Explanation
Likelihood is low-to-moderate: the attacker needs one legitimate `(raw_body, hmac)` pair, which is trivially obtainable by installing the app themselves (a normal, unprivileged flow — no leaked credentials, no `api_secret_key`, no TLS interception required) and capturing the webhook their own shop triggers, then POSTing it again to the same public endpoint with a forged `shop-domain` header.

### Recommendation
Bind the shop/topic identity into the signed payload verification: e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or independently verify that the `shop-domain` header corresponds to a shop with an active session/installation before dispatching to handlers, rather than trusting header-derived `request.shop`/`request.topic` purely because the raw body's HMAC checks out.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any webhook (e.g. `orders/create`) with a small/predictable body (or captures the exact `raw_body` and its Shopify-delivered `X-Shopify-Hmac-Sha256` value).
2. Attacker POSTs to the app's public webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — validation succeeds.
4. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` as shown in [4](#0-3) , causing the host app to act on behalf of `victim-shop.myshopify.com` using attacker-controlled data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
