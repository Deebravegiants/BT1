### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is trusted for tenant identity but is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `Utils::HmacValidator.validate` in `Registry.process` authenticates the body bytes only. The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers that are excluded from the signable string, yet these values — most importantly `shop` — are forwarded unauthenticated into `WebhookMetadata` and used by the host application's handler as the tenant identity for the event. An attacker who can obtain any one genuine, HMAC-valid webhook delivery (e.g., for their own installed shop) can replay it to the app's webhook endpoint with an arbitrary `shop-domain` header, and the gem will accept it as valid and hand the handler an event falsely attributed to a different shop.

### Finding Description
The equality that should hold is:

`bytes verified by HMAC == identity fields acted upon by the handler`

but in this gem it is:

`bytes verified by HMAC (raw_body only) != shop/topic/webhook_id used for dispatch and tenant attribution`

Concretely:
- `Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all pulled straight from attacker-controllable headers with no cryptographic binding to the body: [2](#0-1) 
- `Registry.process` validates only the HMAC of the `Request` (i.e., the body) and then dispatches using `request.topic`/`request.shop`/etc. without any additional binding check: [3](#0-2) 
- `Utils::HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string`, i.e., the body for webhooks: [4](#0-3) 
- The resulting `WebhookMetadata.shop` (and `topic`/`webhook_id`) is precisely the unauthenticated header value, and this is the struct the host application's `WebhookHandler#handle` receives as the trusted tenant identifier for the event: [5](#0-4) 

Because Shopify signs webhooks with a secret shared across every shop that has the app installed, any shop running the app can legitimately obtain one HMAC-valid `(body, hmac)` pair by simply receiving its own real webhook delivery. Since the header set (`shop-domain`, `topic`, `webhook-id`, `api-version`) is completely outside the signed bytes, that same `(body, hmac)` pair remains valid when replayed with a different `shop-domain` header. The gem provides no mechanism to bind the header-derived shop to the signed payload, so it cannot distinguish "this event happened on my shop" from "this event happened on shop X" for any attacker who controls both a valid signature and the ability to call the app's webhook endpoint directly.

### Impact Explanation
This breaks the tenant boundary the app relies on `WebhookMetadata.shop` for. An attacker who has genuinely installed the app on their own store (an unprivileged, non-credentialed relationship to any other tenant) can:
1. Capture one valid `(raw_body, hmac)` pair from a webhook legitimately delivered to their own shop.
2. Re-POST that exact body/HMAC to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop's domain (and optionally forge `topic`/`webhook-id` too, since none of these participate in the signature).
3. `Registry.process` accepts the request as valid (HMAC matches the body) and calls the handler with `WebhookMetadata.shop` set to the victim's domain.

Depending on how the host app uses the shop value from `WebhookMetadata` (e.g., looking up/creating a session, marking the shop uninstalled via `app/uninstalled`, injecting order/customer data via `orders/create`/`customers/create` topics), this is a cross-tenant data-injection or cross-tenant state-corruption primitive attributed entirely to the wrong merchant, satisfying the Critical "cross-tenant access" bar without requiring the `api_secret_key`, any access token, or any credential belonging to the victim.

### Likelihood Explanation
Likelihood is high for any deployment that trusts `WebhookMetadata.shop`/`topic`/`webhook_id` as-is (which is exactly what the struct and its doc-comment promise): the attacker needs only (a) their own legitimate app installation to obtain one valid signed payload, and (b) the ability to send an arbitrary HTTP request to the app's public webhook receiver — no interception, no secret material, no privileged account.

### Recommendation
Bind the header-derived identity fields into the signed material, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the request before trusting them:
- Include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (mirroring how `AuthQuery#to_signable_string` binds `shop`/`host`/`state`), or
- Have `Registry.process` independently verify that the header-derived `shop` matches an expected/authorized shop for the current delivery context before constructing `WebhookMetadata`, and document clearly that consumers must not treat `WebhookMetadata.shop` as authenticated unless such binding is added.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`. Shopify delivers a legitimate webhook, e.g. `app/uninstalled`, to the app's endpoint with headers:
   ```
   X-Shopify-Topic: app/uninstalled
   X-Shopify-Hmac-Sha256: <valid HMAC over the raw body, computed by Shopify with the shared api_secret_key>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   ```
2. Attacker captures the raw body and the `X-Shopify-Hmac-Sha256` value from this delivery.
3. Attacker sends a new HTTP request directly to the app's webhook endpoint, reusing the identical raw body and `X-Shopify-Hmac-Sha256` header, but sets:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` matches because `to_signable_string` only returns `@raw_body`: [1](#0-0) 
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because the body/HMAC pair is unchanged: [6](#0-5) 
6. The registered handler is invoked with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", ...)`, causing the host app to process an uninstall (or any other topic-specific) event for a shop the attacker never controlled: [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
