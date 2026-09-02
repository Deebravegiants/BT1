### Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller's app-supplied `shop-domain` header straight through to the handler as the authenticated tenant identifier. The HMAC never covers that header, so the value used for cross-tenant attribution is not bound to the value that was actually verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` simply reads the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e., the body) [3](#0-2) . `Registry.process` calls this validator and, on success, immediately builds `WebhookMetadata` using `request.shop` — the header value that was never part of the signed material — as the tenant identifier passed to the app's handler [4](#0-3) . `WebhookMetadata#shop` is a plain `String` field with no further validation [5](#0-4) .

This is exactly the identity-binding break called out in scope: "a field acted on but not covered by the HMAC." The equality that should hold is:
`shop attributed to the event == shop whose bytes were authenticated by the HMAC`
but the gem only proves `HMAC(body, client_secret) == received_hmac`; it proves nothing about which shop produced that body. Because a single app's `client_secret` is shared across every merchant that installs the app, any shop with the app installed can compute a valid HMAC over an arbitrary body of its choosing and then send that request to the app's webhook endpoint with a manipulated `shop-domain` header naming a different (victim) shop. `Registry.process` will accept the HMAC as valid and dispatch the handler with `data.shop` set to the attacker-chosen value, even though that value was never authenticated.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as the docs and generated code encourage — it is the only identity Robert/handler receives) to decide which merchant's records to create, update, or delete, an attacker who has legitimately installed the app on their own (attacker-controlled) shop can forge webhook deliveries that are processed as if they originated from a different merchant. This is a cross-tenant identity confusion inside the gem's own webhook-processing API, matching the in-scope "cross-tenant access" impact category, since the trust boundary the gem is supposed to enforce (an event is bound to the shop that generated it) is not actually enforced by any binding in the code.

### Likelihood Explanation
Likelihood is Low/Medium: exploitation requires the attacker to have (or create) a legitimate installation of the same app so they possess a request that the app's shared `client_secret` will validate, and it requires network-level ability to send a crafted HTTP request to the app's public webhook endpoint with a spoofed header (normal delivery is from Shopify's infrastructure, but the endpoint itself is a public URL the app must expose, and nothing in this gem restricts the source IP or re-derives `shop` from any authenticated channel). No leaked credentials, TLS interception, or privileged account are required — only an ordinary merchant/developer account able to install the app.

### Recommendation
Do not treat the `shop-domain` header as authenticated tenant identity on its own. Either:
1. Extend `to_signable_string`/the HMAC computation to bind the shop (and other identity-relevant headers such as `webhook-id`/`api-version`) into the signed payload, or
2. Require host applications/the gem itself to cross-check `request.shop` against a shop for which a session/webhook registration is already known to exist for that specific topic/webhook_id before dispatching the handler, rather than passing the raw header value through unchecked in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own development store `attacker-shop.myshopify.com`, obtaining a shared `client_secret`-signed HMAC capability common to the app (not the secret itself — Shopify computes and delivers this HMAC for legitimate events from the attacker's own shop).
2. Attacker captures one legitimate webhook delivery for their own shop (body `B`, valid `hmac-sha256` header `H = HMAC_SHA256(client_secret, B)`).
3. Attacker POSTs the exact same body `B` and header `H` to the app's public webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` re-computes `HMAC_SHA256(client_secret, B)`, which equals `H`, so validation succeeds [6](#0-5) .
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the app processes the attacker's body as an authenticated event for the victim shop [7](#0-6) .

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
