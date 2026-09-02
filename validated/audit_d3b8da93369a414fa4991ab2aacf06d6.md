### Title
Webhook HMAC signature does not cover the `shop`/`topic` identity headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` validates only the body's HMAC and then trusts these headers to route and attribute the webhook. Because the HMAC key is the single app-wide `client_secret` shared across every shop that installs the app, any body+HMAC pair captured from one (attacker-controlled) shop's webhook remains a byte-for-byte valid signature when replayed with forged `shop`/`topic` headers, breaking the binding between "bytes authenticated by HMAC" and "shop/topic the app acts on."

### Finding Description
`Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 

only the `@raw_body` is included. All other identity fields (`shop`, `topic`, `webhook_id`, `api_version`) are pulled straight from headers with no cryptographic binding: [2](#0-1) 

`Webhooks::Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (i.e., the raw body) against the HMAC header, then immediately trusts `request.topic` and `request.shop` to dispatch and attribute the event: [3](#0-2) 

The HMAC is computed with `Context.api_secret_key`, a single secret shared by the app across *every* installed shop, not a per-shop secret: [4](#0-3) 

**Equality that should hold but doesn't:** `shop_authenticated_by_hmac == shop_used_by_handler`. In reality, the HMAC authenticates only `raw_body`; the `shop` (and `topic`) the handler actually acts on come from headers that are outside the signed byte range. A request with a validly-signed body from shop A can be replayed with an `x-shopify-shop-domain` header claiming shop B, and `HmacValidator.validate` will still return `true` because it only recomputes the digest over the body.

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately installs the app on their own (attacker-controlled) shop can capture one genuine `(raw_body, hmac)` pair from a real webhook Shopify sends them, then replay that exact body to the app's public webhook endpoint while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to claim it belongs to a victim shop. Because `Registry.process` passes `request.shop` straight into `WebhookMetadata` for the handler without any header-level authentication, the host application's webhook handler will process attacker-supplied data under a victim shop's identity — i.e., cross-tenant data injection/spoofing. This matches the "cross-tenant access" critical-impact category, since the trust boundary between merchants is broken using only a public endpoint and a legitimately-obtained webhook from the attacker's own store.

### Likelihood Explanation
Requires only unprivileged capability: install (or use a free/dev) shop of the app to receive one real webhook, capture body+HMAC header, then send crafted HTTP POST requests to the app's public webhook endpoint with forged Shopify headers. No secrets, tokens, or privileged access are needed — the `client_secret` itself is never exposed to the attacker, only reused unmodified by design against a byte range that excludes the identity headers.

### Recommendation
Include the shop domain, topic, and any other fields the application will act on inside the HMAC-signed content (or otherwise cryptographically bind the headers to the body), e.g., verify `x-shopify-hmac-sha256` against `shop-domain + topic + raw_body`, or independently confirm `shop`/`topic` via a second authenticated channel (e.g., cross-check against the shop retrieved from an active, verified session) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on shop `attacker.myshopify.com` and configures a webhook (e.g., `orders/create`).
2. Shopify sends a real webhook POST to the app: body `B`, header `x-shopify-hmac-sha256: H` (computed as `HMAC-SHA256(client_secret, B)`), `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)`.
4. Attacker sends a new POST to the same public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)`, matching `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
6. `Registry.process` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-199`) and invokes the handler, which now processes attacker-controlled data attributed to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
