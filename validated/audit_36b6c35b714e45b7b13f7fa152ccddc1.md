Found it. In `lib/shopify_api/webhooks/request.rb`, the HMAC is verified over `to_signable_string`, which returns the raw request body (`@raw_body`), while the webhook `shop` and `topic` identity used by `Registry.process` and passed to the handler come from **HTTP headers** (`shopify-shop-domain`, `shopify-topic`), which are never covered by the HMAC signature at all. [1](#0-0) 

### Title
Webhook shop/topic identity is not bound to the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `HmacValidator.validate` only proves that the request *body* bytes were signed by Shopify. The `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` uses to select the handler and construct `WebhookMetadata` are read straight from unauthenticated HTTP headers, never included in the signed string.

### Finding Description
`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string`: [2](#0-1) 

`to_signable_string` only returns `@raw_body`: [3](#0-2) 

But `shop`, `topic`, `webhook_id`, `api_version` are pulled from headers, not from the signed body: [4](#0-3) 

The identity binding that should hold is: `hmac(body, secret) == received_hmac` **and** `shop header == shop that produced the body`. Only the first half is checked. Because `shop`/`topic`/`webhook_id` are excluded from `to_signable_string`, the gem cannot detect if a caller sends a validly-signed body from Shop A alongside forged headers claiming Shop B (or a different topic). Whoever controls the transport in front of the endpoint (e.g., a shared/misconfigured reverse proxy, header-injection point, or a malicious actor able to influence headers while replaying/relaying a legitimately-signed body from any tenant) can make `Registry.process` dispatch the handler with `WebhookMetadata.shop` set to an arbitrary value while the HMAC check passes, since the check never touches the header bytes.

### Impact Explanation
This breaks the identity binding `shop-header == shop-that-signed-payload`, letting an attacker cause the handler to process webhook data under an attacker-chosen tenant (`shop`) identity while still passing signature verification — this is a cross-tenant confusion at the trust boundary the gem is responsible for enforcing on behalf of the host app, matching the "High" bucket (scope/binding check bypass leading to cross-tenant handling).

### Likelihood Explanation
Exploitability is conditioned on an attacker being able to influence the HTTP headers reaching `Webhooks::Request.new` (e.g. malformed proxy/CDN configurations forwarding attacker-supplied `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers while the body remains a validly-signed but unrelated payload, or two apps sharing an endpoint). This is a real gap in the gem's own verification logic (the signable string omits shop/topic), independent of host-application behavior, but requires a header-injection/relay vector to fully realize, so likelihood is Medium rather than High.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them, e.g. by validating that the shop domain embedded in the signed JSON body's own top-level fields matches the header value) so that `HmacValidator.validate` proves both the payload integrity and the header-derived identity used by `Registry.process`.

### Proof of Concept
1. Attacker captures/relays a validly HMAC-signed webhook body (e.g. via a shared endpoint, or a proxy that lets header values be attacker-set) for `shop-domain: legit-shop.myshopify.com`.
2. Attacker resends the same raw body but sets header `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
3. `HmacValidator.validate(request)` recomputes `HMAC(body, secret)` — unchanged, since `to_signable_string` only returns `@raw_body` — and the check passes. [3](#0-2) 
4. `Registry.process` looks up the handler by `request.topic` and builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-controlled header values, dispatching the handler under the wrong tenant identity despite the "valid" HMAC. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
