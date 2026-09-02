### Title
Webhook `shop` and `topic` Identity Fields Are Not Covered by the HMAC Signature, Enabling Cross-Tenant Webhook Forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signed payload as only the raw HTTP body: [1](#0-0) 

`to_signable_string` returns `@raw_body` exclusively — it does **not** include the `shop`, `topic`, `webhook_id`, or `api_version` values that are read straight from HTTP headers via `shopify_header`: [2](#0-1) [3](#0-2) 

`Registry.process` validates only this HMAC of the body, then dispatches by `request.topic` and forwards `request.shop` unchecked to the app's webhook handler as trusted tenant identity: [4](#0-3) 

The equality that should hold is: **bytes verified by HMAC == bytes used to establish shop/tenant identity**. Here, HMAC verifies `raw_body` only, while `request.shop` (an unauthenticated header) is what the handler uses to attribute the webhook to a tenant — the field acted on is not covered by the HMAC.

Because the webhook signing secret (`Context.api_secret_key`, i.e., the app's `client_secret`) is shared across *all* shops that install the app, any shop that installs the app receives real webhook deliveries whose `(raw_body, hmac)` pairs are valid under that same shared secret. An unprivileged internet user who controls (or trials) any shop installing the app can capture one legitimate `(raw_body, hmac)` pair from their own store's webhook delivery, then replay it to the app's public webhook endpoint while substituting an arbitrary `shop-domain` (and/or `topic`) header. `HmacValidator.validate` only checks `raw_body` against the secret — it has no way to detect that `shop`/`topic` were swapped — so the forged request passes validation and is processed as if it originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook system is meant to enforce: an attacker with no privileges on the victim shop can inject data attributed to that shop into the host application's webhook handling logic (e.g., triggering shop-scoped business logic, cache invalidation, order/customer processing, or state updates keyed by `data.shop`) using data they control. This matches the Critical "cross-tenant access" impact category, since the shop identity binding that gates per-tenant processing is not cryptographically enforced.

### Likelihood Explanation
Any user who can install the app on at least one shop (including a free/trial development store) can capture valid `(raw_body, hmac)` pairs for the webhook topics they control, then freely relabel and replay them against the same public webhook endpoint with a different `shop-domain` header. No access token, `api_secret_key`, or privileged account is required — only the ability to install the app once and observe a legitimate webhook delivery, which is normal, unprivileged usage of the platform.

### Recommendation
Bind the identity headers into the signed payload used for HMAC verification, not just the body. For example, construct `to_signable_string` (or a companion check) that incorporates `shop`, `topic`, and `webhook_id` alongside the raw body before computing/comparing the HMAC, or otherwise cryptographically bind these values (e.g., verify that the `shop-domain` header matches an expected/allow-listed set of shops for the currently active session/install) before dispatching to the handler. At minimum, document and encourage host applications to independently verify `data.shop` against known installed shops before trusting the payload, but the stronger fix is to make the signature cover the full identity context.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (any store, including a free dev store).
2. Shopify sends a real webhook to the app's endpoint for `attacker-shop.myshopify.com`, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of RAW_BODY under shared api_secret_key>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   RAW_BODY (attacker-controlled order JSON, since it's their own store)
   ```
3. Attacker captures this exact `RAW_BODY` and `x-shopify-hmac-sha256` value.
4. Attacker replays the identical request to the same public webhook endpoint, changing only:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
   keeping `RAW_BODY` and `x-shopify-hmac-sha256` unchanged.
5. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `to_signable_string` (`RAW_BODY` only) and it matches — validation succeeds.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the `orders/create` handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, causing the host application to process attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
