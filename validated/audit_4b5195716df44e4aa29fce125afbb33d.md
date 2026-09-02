## Analysis

The reported bug class—accepting an unauthenticated/unbound field as if it were verified—has a direct analog in this gem's webhook handling. [1](#0-0) 

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers and are never included in the signed content. [2](#0-1) 

`HmacValidator.validate_signature` computes the HMAC only over `verifiable_query.to_signable_string` (the raw body), and compares it to the `hmac-sha256` header. [3](#0-2) 

`Registry.process` validates the HMAC, then immediately trusts `request.shop` to build `WebhookMetadata`, which the host application's handler uses to know which merchant/tenant the event belongs to.

### Title
Webhook `shop` header is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/verifies the HMAC over the raw body only. The `shop-domain` (and `topic`, `webhook_id`, `api-version`) headers are read independently and are not part of the signed payload. Since Shopify signs webhooks using the app's `client_secret`, which is identical for every shop that has the app installed, any merchant who installs the app can capture a legitimate `(raw_body, hmac)` pair from their own shop's webhook traffic and replay it to the app's webhook endpoint with an arbitrary `shop-domain` header value. The signature still validates because it only covers the body, so the forged `shop` field is accepted and passed on to the handler as authentic.

### Finding Description
The identity binding that should hold is:
`shop header verified by HMAC == shop value the handler attributes the event to`

In this gem that equality is broken:
- Before request: Shopify computes `hmac = HMAC(client_secret, raw_body)` and sends it along with `shop-domain: legit-shop.myshopify.com` for a specific install.
- Attacker capture: An unprivileged user who installs the app on their own shop (`attacker.myshopify.com`) receives genuine webhooks for their own store, each with a valid `(raw_body, hmac)` pair signed with the same app-wide `client_secret`.
- Attacker's forged request: They resend the same `raw_body`/`hmac` pair to the app's webhook endpoint but substitute `shop-domain: victim-shop.myshopify.com` (or any other shop using the app).
- After request: `HmacValidator.validate` only recomputes the HMAC over `raw_body` [4](#0-3)  — it still matches, since the body and hmac weren't altered. `Registry.process` then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [3](#0-2)  using the attacker-supplied `shop` value, which the host app's handler will treat as authentic.

This is a direct analog of the report's root cause: a value (`payment_decimals`/`payment_feed_type` there, `shop` here) is taken from unauthenticated input and used downstream without being cryptographically bound to the verified data.

### Impact Explanation
Applications built on this gem key their tenant-scoped business logic (order sync, data updates, uninstall handling, credential/session revocation, etc.) off `WebhookMetadata#shop`. Because `shop` is not covered by the signature, an attacker who is merely a legitimate installer of the app on their own store can forge webhook events that are processed as if they originated from a different merchant's shop — a cross-tenant identity confusion that can corrupt or manipulate another tenant's state within the host application, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a normal, unprivileged merchant capable of installing the target app on their own store (a routine action, no special access, no leaked secrets, no TLS interception). Capturing their own valid `(body, hmac)` pairs and replaying them with a different `shop-domain` header is trivial and requires no cryptographic material beyond what Shopify legitimately sends them.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) values into the signed content verified by `HmacValidator`, or otherwise cryptographically tie the claimed `shop-domain` header to the signature (e.g., include it in `to_signable_string`), so that a replayed body cannot be reattributed to an arbitrary shop.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers any webhook event and captures the resulting request: `raw_body`, and headers `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain`.
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body` [4](#0-3) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, and the host app processes it as a legitimate event for the victim's tenant.

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
