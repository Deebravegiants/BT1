## Title
Webhook Shop/Topic Header Spoofing via HMAC Binding Gap — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC signature exclusively to the raw request body, while the `shop`, `topic`, and `webhook_id` values used downstream by the webhook processor are read from unauthenticated HTTP headers that are never included in the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all parsed straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), which are not part of the signable string: [2](#0-1) 

`Registry.process` validates only the HMAC over `to_signable_string` (i.e., the raw body), then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` taken from headers to route and label the event: [3](#0-2) 

The identity binding that should hold is: `bytes verified by HmacValidator == bytes that determine shop/topic/webhook_id used by the handler`. Because the signature only covers `@raw_body`, and `shop`/`topic`/`webhook_id` come from headers outside that scope, this equality does not hold — the header fields are unauthenticated with respect to the signature. Shopify's real webhook signing scheme signs only the body by design, but that means any consumer of this library that keys shop-scoped logic off `request.shop` (as the bundled `WebhookMetadata` and `process` method do) is trusting a value with no cryptographic binding to the verified bytes.

### Impact Explanation
A user who legitimately receives one authentic, HMAC-signed webhook for their own shop (e.g., by installing the app and triggering an `orders/create` event) can capture that raw body and its valid HMAC, then replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different (victim) shop and/or a different `X-Shopify-Topic`. `Utils::HmacValidator.validate(request)` will still pass because it only checks the raw body against the secret; `Registry.process` will then hand the (attacker-chosen, real) payload to the handler registered for the spoofed topic, tagged with the spoofed shop in `WebhookMetadata`. Any host application that uses `WebhookMetadata#shop` to select tenant context, write to a shop-scoped store, or route to shop-specific business logic will process attacker-controlled data under an incorrect tenant identity — a cross-tenant confusion attack requiring no privileged credentials.

### Likelihood Explanation
This requires only that the attacker be a merchant/user who can install the app (or otherwise receive at least one legitimately signed webhook for their own shop) and can send arbitrary POST requests with custom headers to the app's public webhook endpoint — no `api_secret_key`, access token, or other privileged material is needed, since the replayed body/HMAC pair is already valid. It relies on host applications trusting `request.shop`/`request.topic` for tenant-scoping, which is the documented/intended usage of `Webhooks::Registry`.

### Recommendation
- Bind the shop, topic, and webhook id into the verified signable content, or otherwise cryptographically tie the headers to the signed body (e.g., include them in a canonicalized signable string, or require the caller to independently verify the `shop-domain` header against the session/tenant the request arrived on).
- At minimum, document prominently that `request.shop`/`request.topic`/`request.webhook_id` are unauthenticated relative to the HMAC and must not be used for tenant routing without additional verification (e.g., cross-checking against a known/expected shop for the endpoint).
- Consider validating that `request.shop` matches an expected/allow-listed shop domain for the given HMAC secret before dispatching to handlers.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com` and trigger a webhook event (e.g., `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends — this HMAC is valid because it signs only the raw body.
2. Replay this exact `(raw_body, hmac)` pair to the app's webhook endpoint, but change the `X-Shopify-Shop-Domain` header to `victim.myshopify.com` (and optionally `X-Shopify-Topic` to a different registered topic).
3. `Utils::HmacValidator.validate(request)` at `Registry#process` succeeds because it only checks `raw_body` against the secret: [4](#0-3) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: <spoofed topic>, body: <attacker's real order data>, ...)`, causing any shop-scoped processing in the host app to act on the wrong tenant.

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
