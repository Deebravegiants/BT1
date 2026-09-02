Confirmed: `to_signable_string` for `Webhooks::Request` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Registry.process` are all read straight from HTTP headers via `shopify_header`, which are never included in the signed payload [3](#0-2) [4](#0-3) .

### Title
Webhook `shop` (tenant) identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator` verifies the HMAC solely against that body. The `shop`, `topic`, `webhook_id`, and `api_version` fields are pulled from HTTP headers that are never part of the signed content, so `Registry.process` passes an unauthenticated `shop` value to the application's webhook handler.

### Finding Description
`Registry.process` validates a webhook by calling `Utils::HmacValidator.validate(request)` [5](#0-4) . `HmacValidator.validate_signature` computes `OpenSSL::HMAC.hexdigest(...secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header value [2](#0-1) . For `Webhooks::Request`, `to_signable_string` returns `@raw_body` only [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers respectively via `shopify_header` [3](#0-2) .

After HMAC validation succeeds, `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and dispatches it to the registered handler unconditionally [6](#0-5) . Because `shop` is never part of the signed material, the equality the gem implicitly claims — "shop delivering a validly-signed webhook" == "shop asserted in the `shopify-shop-domain` header" — does not hold. Any two requests differing only in the `shop`/`topic`/`webhook_id` headers but sharing the same `raw_body` and `hmac` will both pass `HmacValidator.validate`.

### Impact Explanation
A host application typically uses `WebhookMetadata#shop` returned by this gem to resolve which merchant/tenant the webhook body applies to (e.g., to look up that shop's session or perform tenant-scoped writes/deletes), trusting that a valid HMAC implies the header-derived `shop` is authentic. Since `shop` is outside the signed scope, an attacker who obtains any single valid `(raw_body, hmac)` pair — for example from their own store's webhook deliveries, which they control and can trigger themselves without any special privilege — can resend that exact body/HMAC combination while substituting an arbitrary `shopify-shop-domain` (and `topic`) header value. The gem will report the webhook as valid and hand the handler a `shop` value chosen by the attacker, enabling cross-tenant confusion in any application logic keyed off `WebhookMetadata#shop`.

### Likelihood Explanation
Exploitation only requires the ability to send an HTTP POST to the app's webhook endpoint with attacker-controlled headers and a previously-observed valid body/HMAC pair (trivially available to any merchant on their own store, which is an unprivileged actor relative to other tenants). No access token, `client_secret`, or privileged credential is required — only a replayed body and forged headers.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the string that is HMAC-verified (or otherwise cryptographically bind them to the signed body), so that `Utils::HmacValidator.validate` rejects any request whose header-derived identity fields do not match what was originally signed by Shopify.

### Proof of Concept
1. Attacker owns/operates `attacker-shop.myshopify.com` and registers a webhook handler on the target app.
2. Shopify sends a legitimate webhook to the app for `attacker-shop.myshopify.com` with body `B` and a valid header `shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker replays the exact same POST to the app's webhook endpoint, but changes `shopify-shop-domain` to `victim-shop.myshopify.com` (and, if desired, `shopify-topic`/`shopify-webhook-id`), leaving `B` and the `hmac` header unchanged.
4. `Registry.process` calls `HmacValidator.validate`, which recomputes the HMAC over `B` only — validation succeeds since `B` and the HMAC are unchanged.
5. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the app's handler, which processes attacker-controlled body content under the identity of `victim-shop.myshopify.com`.

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
