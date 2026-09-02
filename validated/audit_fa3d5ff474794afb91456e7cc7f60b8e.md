### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request **body**. The `shop` identity that is forwarded to the app's webhook handler is read from the `X-Shopify-Shop-Domain` HTTP **header**, which is never included in the HMAC-signed content. This breaks the identity binding `hmac-verified-bytes == identity-used-by-handler`: the signature only proves the body came from someone holding the app's shared secret, it proves nothing about which shop the event belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are parsed straight from headers and are not part of that signable string: [2](#0-1) 

`Registry.process` validates only the HMAC computed by `HmacValidator` over `to_signable_string` (the body), then unconditionally trusts `request.shop` and passes it straight to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` only ever signs/compares `verifiable_query.to_signable_string`, i.e., the body: [4](#0-3) 

Because the shared secret (`Context.api_secret_key`) is the **same secret for every shop** that has installed the app, any merchant who has installed the app on their own store can:
1. Trigger a webhook event on their own store and capture the legitimate `(raw_body, X-Shopify-Hmac-SHA256)` pair Shopify sends them (this uses only their own, unprivileged merchant access — no `api_secret_key`, no access token theft required).
2. Replay that exact `raw_body` + `hmac` to the app's public webhook endpoint, but substitute a victim shop's domain in the `X-Shopify-Shop-Domain` header.
3. `HmacValidator.validate` still succeeds because it only checks body+hmac, and `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` using the attacker-controlled header value, calling the handler as if the event belonged to the victim shop.

This is the exact bug class from the reference report: a field (`shop`) that is *acted upon* (used as the tenant identity dispatched to the handler) is not covered by the integrity check (HMAC over body only), letting an attacker who controls one side of the binding (a valid signed payload from their own tenant) forge the other side (the tenant identity) freely.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` to key per-tenant state (e.g., update billing, cancel subscription, disable app, write shop-scoped data, invalidate sessions) can be made to apply attacker-supplied event data to an arbitrary victim shop. This is a cross-tenant access/integrity violation: an unprivileged merchant can inject fabricated events attributed to any other shop simply by knowing/guessing the victim's `myshopify.com` domain (which is not secret).

### Likelihood Explanation
High likelihood for any app that trusts `WebhookMetadata#shop` as an authenticated identity (which the gem's own documentation instructs developers to rely on) — no special privileges, tokens, or knowledge of the secret are required, only the ability to install the app once on any shop (including the attacker's own) and send an HTTP request to the app's public webhook endpoint.

### Recommendation
Bind the header-derived `shop` (and `topic`/`webhook_id`) into the value covered by the HMAC check, e.g., include the `X-Shopify-Shop-Domain` header in the signable string alongside the body, or perform a secondary check that the topic/shop combination is consistent with a registration the app expects for that shop before dispatching to the handler.

### Proof of Concept
1. Install the app on shop A (attacker-controlled) and trigger any webhook topic the app has registered for.
2. Capture the resulting `raw_body` and `X-Shopify-Hmac-SHA256` header from the real delivery.
3. POST to the app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-SHA256`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. Observe that `ShopifyAPI::Webhooks::Registry.process` accepts the request (HMAC over body validates) and invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, using attacker-controlled body content attributed to the victim tenant. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
