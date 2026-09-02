### Title
Webhook HMAC validation covers only the raw body, not the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates incoming webhooks by validating an HMAC signature, then dispatches the webhook to the registered handler along with a `shop` value taken from the request. However, the HMAC signature only covers the raw request body — it does **not** cover the `shop-domain` (or `topic`/`webhook-id`) header that is passed to the handler. This breaks the intended binding `HMAC-authenticated bytes == identity attributed to the event`, letting an attacker who possesses *any* valid `(body, hmac)` pair for the shared secret relabel that payload as belonging to an arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

Meanwhile, `shop`, `topic`, and `webhook_id` are all read straight from unauthenticated HTTP headers: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this validation result to gate the whole request, then forwards the **header-derived, unauthenticated** `shop`, `topic`, and `webhook_id` to the app's handler: [4](#0-3) 

Because the HMAC is computed purely from the shop's api secret (shared across *all* shops that install the app) and the raw body, and the body content is not shop-specific in its signature computation, the same `(body, hmac)` pair is valid regardless of which shop's `x-shopify-shop-domain` header accompanies it. The identity binding that should hold is:

`shop authenticated by HMAC == shop attributed to the processed webhook event`

but this gem only proves "some entity possessing the api_secret_key produced this body," and separately, unconditionally trusts the `shop-domain` header for tenant attribution. These two values are never cross-checked.

### Impact Explanation
An attacker who is a legitimate, unprivileged installer of the app on their own shop receives genuine webhooks with valid `(raw_body, hmac)` pairs for their own store. Because the HMAC never binds the shop domain, they can replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with any victim shop's domain. `Utils::HmacValidator.validate` will still succeed (it only checks the body against the secret), and the handler will receive `WebhookMetadata` attributing the attacker's payload to the victim shop. Depending on how the host application keys its business logic off `shop` (e.g., updating billing/subscription state, order/inventory records, or session data per shop), this enables cross-tenant data corruption or unauthorized actions performed in another merchant's context — a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires only that the attacker run the target app on a shop they control (a normal, unprivileged install) and observe at least one legitimate webhook delivery — no access to `api_secret_key`, access tokens, or TLS interception is required. Any host application that trusts `WebhookMetadata#shop` for tenant scoping (the documented/intended usage) is affected. This is a straightforward, low-effort attack once the app is installed.

### Recommendation
Include the identity fields that are used for authorization decisions — at minimum `shop`, and ideally `topic` and `webhook_id` — in the HMAC-signed content, or verify them out-of-band (e.g., cross-check the header shop against a shop the app has an active session/installation for) before trusting `WebhookMetadata#shop`. Concretely, change `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to bind these header values so a valid signature can only be replayed for the exact shop and topic it was generated for, e.g.:

```ruby
def to_signable_string
  "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
end
```
(matching whatever canonicalization Shopify's own signing process would need to support) — or, at minimum, document that host applications must independently verify `shop` against a known/authorized shop list rather than trusting it as authenticated.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook delivery, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Webhook-Id: abcd-1234

   {"id": 1, "amount": 100}
   ```
2. Replay the identical body and `X-Shopify-Hmac-Sha256` value, but change the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac-for-same-body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: abcd-1234

   {"id": 1, "amount": 100}
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, raw_body)`: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload originated from the attacker's own shop, demonstrating the cross-tenant identity binding break.

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
