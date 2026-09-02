### Title
Webhook `shop-domain` header is trusted and forwarded to app handlers without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity using `Utils::HmacValidator.validate(request)`, but the HMAC signable string for a webhook `Request` is defined as only the raw request body [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers and are never included in the signed data [2](#0-1) , yet `Registry.process` forwards these header-derived values directly to the app's handler as trusted identity/context for the webhook [3](#0-2) .

### Finding Description
The equality that should hold is: `shop header value == shop that actually produced/owns the HMAC-signed body`. Because `to_signable_string` only returns `@raw_body` [1](#0-0) , `HmacValidator.validate_signature` computes and compares the HMAC solely over the body bytes [4](#0-3) . The `shop-domain`, `topic`, and `webhook-id` headers are read via `shopify_header` with no cryptographic binding to that signature [5](#0-4) .

`Registry.process` raises only if the HMAC over the body fails, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`, and dispatches it to the registered handler [3](#0-2) . Any party that can obtain one genuine `(body, hmac)` pair for the app's shared `api_secret_key` — e.g. by installing the app on their own shop (an unprivileged, self-serve action for any public/embedded app) and receiving a real webhook for an event they themselves triggered — can replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a different, victim shop. `Utils::HmacValidator.validate` will still return `true` because it only checks the body against the secret, so `Registry.process` accepts the request and hands the handler attacker-controlled body content labeled as belonging to the victim shop.

This is the same missing-binding bug class as the report: a value that is *acted upon* downstream (`shop` used to attribute/route webhook data, analogous to the highest-bidder identity used to gate cancellation) is not included in the check that is supposed to guarantee its authenticity (the HMAC, analogous to the missing highest-bidder guard in `_cancelAllBids`).

### Impact Explanation
This breaks the shop/tenant identity binding, letting an attacker who controls one shop's app installation inject data attributed to an arbitrary victim `shop` domain into the host application's webhook handler. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up per-shop session/access tokens or to write into per-shop records), this can result in cross-tenant data corruption or cross-tenant state confusion, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (unprivileged) installer of the target app on their own shop — no leaked secrets, no privileged account, and no TLS interception are required. They need one authentic webhook delivery (trivial to trigger, e.g. by performing an action on their own store that fires a subscribed topic) and the ability to send an arbitrary HTTP POST with modified headers directly to the app's public webhook endpoint (also trivial, since that endpoint must be internet-reachable to receive Shopify's webhooks).

### Recommendation
Bind the shop/topic identity into the authenticated data before trusting it: either (a) include `shop`, `topic`, and `webhook_id` in the HMAC signable string/verification (would require Shopify's platform-side signing to change), or (b), practically within this gem, require callers/`Registry.process` to cross-check `request.shop` against an independently trusted source (e.g., the session store keyed by shop that the app already maintains, or the webhook subscription registered for that `webhook_id`) before invoking the handler, and document that the `shop` header must never be trusted solely because the body HMAC validated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (self-serve, no privileges needed).
2. Attacker triggers a subscribed webhook topic (e.g. `orders/create`) on their own store, capturing the genuine `raw_body` and its `X-Shopify-Hmac-Sha256` header value sent by Shopify (signed with the app's shared `api_secret_key`).
3. Attacker POSTs this exact `raw_body` + `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only look at the body [6](#0-5) , so `Utils::HmacValidator.validate(request)` returns `true` in `Registry.process` [7](#0-6) .
5. `Registry.process` calls `handler.handle` with `shop: "victim-shop.myshopify.com"` and the attacker-authored body, even though that body was never produced by or for the victim shop [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-13)
```ruby
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
