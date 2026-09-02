Confirmed: `Utils::HmacValidator.validate(request)` checks the HMAC only against `to_signable_string`, which for `ShopifyAPI::Webhooks::Request` returns `@raw_body` alone [1](#0-0) . The `topic`, `shop`, and `webhook_id` values used downstream are read directly from HTTP headers that are never included in the signed material [2](#0-1) . `Registry.process` validates only this body-only HMAC and then dispatches the handler using the unauthenticated header values for `shop` and `topic` [3](#0-2) .

### Title
Webhook HMAC only signs the request body, not the `shop-domain`/`topic`/`webhook-id` headers, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body, so the HMAC signature Shopify sends only authenticates the body bytes. The `shop-domain`, `topic`, and `webhook-id` headers, which `Registry.process` uses to route and label the event to a specific merchant, are never covered by that signature.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, body || shop || topic)`, i.e., the signature should bind the body to the specific shop/topic it claims to represent. Instead, the gem computes:

- Signed bytes: `to_signable_string` = `@raw_body` only [1](#0-0) 
- Values acted upon: `topic`, `shop`, `webhook_id` read from headers, entirely outside the signed bytes [2](#0-1) 
- Validation: `HmacValidator.validate(request)` recomputes HMAC over `to_signable_string` and compares to the `hmac` header, never touching `shop`/`topic`/`webhook_id` [4](#0-3) 
- Dispatch: `Registry.process` validates the HMAC, then builds `WebhookMetadata` directly from the unauthenticated `request.topic` and `request.shop` [3](#0-2) 

Because a real Shopify webhook body/HMAC pair for shop A (any legitimate webhook the attacker can trigger for their own store, e.g. an order placed in their own dev shop) is a valid `(raw_body, hmac)` pair independent of headers, an unprivileged internet user who controls their own shop can capture that pair and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop and/or the `topic` header changed to a different (attacker-chosen, registered) topic. `HmacValidator.validate` still succeeds because it only checks the body bytes, and the handler is invoked believing the event genuinely originates from and pertains to the victim shop/topic.

### Impact Explanation
This breaks the tenant boundary that webhook processing is supposed to enforce: the HMAC is meant to prove "this body update was sent by Shopify for shop X, topic Y," but it only proves "this body was sent by Shopify for some shop/topic." An attacker can make the host application process a forged event as if it belongs to another merchant, e.g. triggering `WebhookMetadata` with `shop: <victim>` and an attacker-chosen topic (as long as it's registered by the app) while carrying attacker-controlled body content that was actually signed for a different context. Depending on how the host app's `WebhookHandler` acts on `shop`/`topic`/`body` (data sync, redaction, uninstall bookkeeping, entitlement changes), this enables cross-tenant data corruption or unauthorized actions attributed to a shop the attacker doesn't own.

### Likelihood Explanation
Requires only: (1) an attacker's own registered shop that can trigger the app's own webhooks (freely obtainable via a Shopify dev/partner store), and (2) the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint (the app's own endpoint is by definition internet-reachable to receive Shopify webhooks). No access to `client_secret`, no leaked credentials, and no privileged account is needed — the whole point of the HMAC is to let an *unauthenticated* caller be treated as Shopify, and this gem's checked scope is narrower than what it's relied upon for.

### Recommendation
Bind the header fields consumed by `Registry.process` into the signed material, or validate them out of band against the payload data itself. Concretely, `WebhookMetadata`/routing should either derive `shop`/`topic` from within the signed body (Shopify webhook payloads generally include enough info, or an app-specific claim could be added), or `to_signable_string` should incorporate the `shop-domain`, `topic`, and `webhook-id` headers into what's HMAC-verified, rejecting the request if any of them don't match what Shopify actually signed.

### Proof of Concept
1. Attacker registers a Shopify dev store S_attacker and installs the target app, causing the app to register a webhook (e.g., `orders/create`) with the app's endpoint.
2. Attacker performs an action in S_attacker that triggers that webhook; Shopify sends `raw_body`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: s_attacker.myshopify.com`, `x-shopify-topic: orders/create` to the app.
3. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and/or a different registered `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC [5](#0-4) .
5. The registered handler for that topic is invoked with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though the signed payload never had anything to do with `victim.myshopify.com` [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
