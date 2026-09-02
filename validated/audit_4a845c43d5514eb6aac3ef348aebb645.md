Confirmed: `WebhookMetadata` carries `shop`, `topic`, and `webhook_id` straight from the unauthenticated request headers into the handler's trust boundary.

### Title
Webhook shop/topic identity not bound to HMAC allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches to the app's handler using `shop`, `topic`, and `webhook_id` values read from HTTP headers that are never covered by that HMAC. Any party who can obtain one valid `(raw_body, hmac)` pair (e.g. by installing the app on their own store and triggering a real webhook) can replay that exact body/HMAC pair to the app's public webhook endpoint while freely substituting the `shop-domain`, `topic`, and `webhook-id` headers, and the signature check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `api_version`, and `webhook_id` are all read from unauthenticated request headers with no cryptographic tie to the HMAC: [2](#0-1) 

`HmacValidator.validate` (and `validate_signature`) computes the signature purely from `verifiable_query.to_signable_string` (the body) against the app's `api_secret_key`: [3](#0-2) 

`Registry.process` uses this single check as the entire authentication gate, then immediately trusts the header-derived `request.topic` for handler dispatch and `request.shop` for identity, packaging them into `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

The broken identity binding, stated as an equality that the code assumes but never enforces:
`shop/topic/webhook_id delivered to the handler` == `shop/topic/webhook_id authenticated by the HMAC`

In reality, the right-hand side is always empty — the HMAC authenticates zero header fields — so the equality never holds, and the left-hand side is fully attacker-controlled as long as the attacker supplies *some* valid `(body, hmac)` pair.

### Impact Explanation
Because the shop/topic/webhook-id headers ride outside the signed content, an attacker who legitimately installs the app on their own store (an unprivileged, non-victim tenant) can capture one genuine webhook delivery `(raw_body, hmac)` from Shopify to the app's endpoint, then replay that identical body+hmac to the same endpoint while changing:
- `shop-domain` to an arbitrary victim shop's domain, causing the handler to process attacker-chosen body content under a spoofed victim identity, and/or
- `topic` to a different registered topic, causing the same signed body to be routed to and processed by an unrelated handler (e.g. a `customers/data_request` body being replayed as `orders/create`).

This is a cross-tenant identity/authorization confusion: it lets an unprivileged actor make the app believe attacker-controlled webhook data originated from, and pertains to, a shop/topic that was never actually associated with that data. Depending on what the host app's handlers do with `data.shop`/`data.topic`/`data.body` (e.g. writing order/customer records, revoking access, updating billing state), this can lead to cross-tenant data corruption or business-logic bypass driven entirely by an outsider.

### Likelihood Explanation
Exploitability requires only that an attacker be able to run the app on any single Shopify store (or otherwise legitimately trigger one webhook delivery) to harvest a valid `(body, hmac)` pair, and that the app's public webhook endpoint accepts arbitrary headers — both of which hold for any standard Rack/HTTP front end wrapping `ShopifyAPI::Webhooks::Request`/`Registry.process` exactly as documented. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind the identity fields into the authenticated material instead of trusting raw headers post hoc:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signed string (`to_signable_string`) so any tampering invalidates the signature, or
- Independently verify `shop` against the session/shop the webhook was registered for before dispatch, and reject topics that don't match the registration the delivery is claimed to belong to.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it trigger a real webhook, e.g. `carts/update`, capturing the exact `raw_body` and `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and same `hmac` header, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: orders/create` (or any other topic registered by the app)
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only, matches successfully, and `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler registered for `orders/create` with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker body>)`, even though this body/topic/shop combination was never actually sent by Shopify for that shop or topic.

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
