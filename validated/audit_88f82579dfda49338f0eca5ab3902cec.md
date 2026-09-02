### Title
Webhook HMAC does not cover shop/topic/webhook-id headers, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers and passed straight through to the app's webhook handler. Because the app's HMAC secret is shared across every shop that installs the app, any user who installs the app on a store they control can capture a validly-signed webhook, then replay the identical body/HMAC pair while swapping the `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) header to impersonate a different, victim shop.

### Finding Description
The `VerifiableQuery` interface requires an `hmac` and a `to_signable_string`, and `Utils::HmacValidator.validate` verifies that `HMAC(secret, to_signable_string) == hmac`. [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled from separate, unsigned headers: [3](#0-2) 

`Registry.process` validates only the body HMAC and then forwards these unauthenticated fields directly to the application's handler as trusted identity data: [4](#0-3) 

The equality the gem is implicitly asserting is: `hmac_valid(raw_body) == shop_header_is_authentic`. That equality does not hold — the HMAC binds only the body bytes, not the shop/topic/webhook-id metadata that the handler treats as authoritative. Since the API secret used to sign webhooks is per-app (not per-shop), any actor who can install the target app on a shop they control receives legitimately-signed webhook deliveries. They can then re-POST the exact same `raw_body` + `x-shopify-hmac-sha256` value to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with a victim shop's identifier. `HmacValidator.validate` still succeeds because it only checks the body, and the forged `shop`/`topic` values reach the handler as `WebhookMetadata#shop` / `#topic`, unmodified.

### Impact Explanation
This breaks the tenant boundary the webhook handler relies on for attributing incoming events to the correct shop: an attacker-controlled shop's webhook body can be relabeled as belonging to an arbitrary target shop. Depending on how the host application's webhook handler uses `data.shop` (e.g., looking up a session/access token for that shop and acting on it, or writing attacker-supplied body content into per-shop records), this can result in cross-tenant data corruption or cross-tenant actions being taken under another merchant's identity — matching the "cross-tenant access" High/Critical impact class.

### Likelihood Explanation
Exploitation only requires the ability to install the target app on any shop (including a free/dev store) to obtain a genuinely-signed webhook payload, and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with modified headers — no access token, `client_secret`, or privileged account is required. This is a realistic, unprivileged-internet-user attack path.

### Recommendation
Include the shop domain (and topic/webhook-id, if they are relied upon by handlers) in the signed content, or otherwise independently authenticate the shop associated with a webhook (e.g., by validating it against a known/registered shop for the given webhook subscription) rather than trusting the `x-shopify-shop-domain` header solely because the raw body's HMAC matched.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a webhook (e.g., `app/uninstalled`) signed with the app's shared secret.
2. Attacker captures the raw body and the `x-shopify-hmac-sha256` header from this legitimate delivery.
3. Attacker POSTs to the app's webhook endpoint reusing the same raw body and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), despite the payload actually originating from the attacker's own shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
