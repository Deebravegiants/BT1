### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only the raw request body: [1](#0-0) 

The HMAC that is verified (`hmac` accessor, sourced from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header) is checked against `compute_signature(verifiable_query.to_signable_string, secret)`: [2](#0-1) 

Because `to_signable_string` returns only `@raw_body`, none of the other identifying headers — `shop`, `topic`, `webhook_id`, `api_version` — are covered by the signature at all: [3](#0-2) 

`Registry.process` validates only that HMAC-over-body check, then forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight to the app's handler as trusted metadata: [4](#0-3) 

Since a single Shopify app's `api_secret_key` is shared across every shop that installs the app, any unprivileged party who controls a shop with the app installed (e.g., a free/dev-store install) will legitimately receive real webhook deliveries — real `(raw_body, hmac)` pairs signed with the app's shared secret. That party can replay the exact same `raw_body` and `hmac` to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic`, `shopify-webhook-id`) with an arbitrary victim shop's domain. `HmacValidator.validate` will still pass, because the signature only ever covered the body, and `Registry.process` will invoke the handler believing the webhook belongs to the victim shop.

This breaks exactly the identity binding called out for this class of bug: **shop authenticated (bytes actually verified by HMAC) ≠ shop the app acts on (`shopify-shop-domain` header, never covered by the HMAC)**.

### Impact Explanation
Any app built on this gem that uses the `shop` value from `WebhookMetadata` to select which merchant's data/session/state to update (a extremely common pattern for webhook handlers) can be tricked into attributing another tenant's webhook to a different tenant, or attributing a low-privilege tenant's crafted body to a high-value victim shop. This is a cross-tenant confusion primitive rooted entirely in this gem's `Webhooks::Request`/`Registry` design (`to_signable_string` scope, and lack of any header-consistency check before dispatch), independent of how any specific host app chooses to use the metadata — i.e. it is not merely "host app ignoring documented behavior," it is this gem exposing unauthenticated, unbound identity fields as if they were verified.

### Likelihood Explanation
Requires only:
1. The ability to install the target app on any shop (including a free dev store) to legitimately harvest one valid `(raw_body, hmac)` pair, and
2. The ability to send an arbitrary HTTP request to the app's public webhook endpoint with attacker-chosen headers.

No access token, `client_secret`, or `api_secret_key` is ever needed — the attacker never has to compute or know the HMAC secret, since they replay a genuinely signed body they received themselves. This is squarely "unprivileged internet user" territory.

### Recommendation
Bind the identifying headers into the signed payload verification path, e.g. by having `Webhooks::Request#to_signable_string` incorporate `shop`, `topic`, and `webhook_id` alongside the raw body (or by independently validating that the `shop` header corresponds to a shop with a known, active session/install before dispatching to handlers). At minimum, document and enforce that `shop`/`topic`/`webhook_id` must never be trusted for authorization decisions without an out-of-band lookup, since they are not covered by `Utils::HmacValidator.validate`.

### Proof of Concept
1. Install the target app on Shop A (attacker-controlled) and capture a real webhook delivery, e.g. `orders/create`, noting `raw_body` and the `x-shopify-hmac-sha256` header value — both signed with the app's shared `api_secret_key`.
2. Send a new POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but with `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic` if the handler dispatch only inspects header value, not schema).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because only `raw_body` was ever signed: [5](#0-4) 
4. The handler executes believing the event is attributed to `victim-shop.myshopify.com`.

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
