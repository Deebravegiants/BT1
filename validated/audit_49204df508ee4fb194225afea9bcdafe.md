### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `Utils::HmacValidator.validate` authenticates *only the body bytes*, not the `shop-domain`, `topic`, or `webhook-id` headers that `Registry.process` later trusts and forwards to the app's handler as the tenant identity.

### Finding Description
The equality that should hold is: `bytes verified by HMAC == bytes acted upon for tenant attribution`. In this gem it does not: [1](#0-0) 
computes the signable string strictly from `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers with no relation to the signed content: [2](#0-1) 

`Registry.process` validates only that the (headers-independent) body HMAC is correct, then immediately builds `WebhookMetadata` from the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` and dispatches it to the host app's handler: [3](#0-2) 

Because an app's HMAC secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is shared across *every* shop that has the app installed — it is not per-tenant — any merchant that installs the app can legitimately receive a webhook from Shopify for their own store and thus obtain a body + valid HMAC pair signed with that shared secret. Since the `shop-domain` header is never part of the signed content, the attacker (a malicious installer of the app) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `topic`, `webhook-id`) with a victim tenant's identifiers. `HmacValidator.validate` still succeeds because it only recomputes the signature over `@raw_body`: [4](#0-3) 

The `WebhookMetadata` struct passed to the handler then carries an attacker-chosen `shop` value alongside a validly-signed body: [5](#0-4) 

### Impact Explanation
This is a cross-tenant data-integrity break: a host application that uses `WebhookMetadata#shop` (as documented/intended, see `handler.handle(data: WebhookMetadata.new(... shop: request.shop ...))`) to route/attribute incoming webhook data to a specific merchant's tenant record will process attacker-supplied body content under an arbitrary victim shop's identity, since the gem provides no cryptographic guarantee binding `shop` to the signed payload. This matches the "Critical — cross-tenant access" impact category, since a merchant using their own legitimately signed webhook can inject data attributed to a completely different tenant.

### Likelihood Explanation
Likelihood is realistic but requires: (1) the attacker to be a legitimate installer of the target app (an "unprivileged internet user" relative to *other* tenants, but not relative to Shopify's platform-level webhook delivery), and (2) knowledge/reuse of a webhook body whose content is attacker-influenceable or at least replayable (e.g., replaying their own store's `orders/create` webhook body against a victim's shop domain, or crafting a body of an event type they control on their own store). No access token, `client_secret`, or TLS interception is required — only the ability to receive one legitimate webhook for their own shop and resend an HTTP POST to the app's public webhook endpoint with a modified header.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC-signed content (or otherwise cryptographically bind them, e.g. by validating them against Shopify's out-of-band webhook metadata/mTLS if available), so that `HmacValidator.validate` fails whenever these header values are altered from what Shopify originally signed for. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are **not** integrity-protected by `Utils::HmacValidator.validate`, so host applications do not implicitly trust them for tenant attribution.

### Proof of Concept
1. App "AppX" is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both sharing the same `Context.api_secret_key`.
2. Shopify delivers a legitimate webhook to AppX for `attacker-shop.myshopify.com`:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <valid-hmac-of-body>
   shopify-shop-domain: attacker-shop.myshopify.com
   shopify-webhook-id: abc-123
   Body: {"id": 1, "note": "hello"}
   ```
   The attacker captures this raw body and its HMAC (they control the shop, so they can trigger events with attacker-chosen content, e.g. an order `note`).
3. Attacker resends the identical body and HMAC to AppX's webhook endpoint, but changes only the `shopify-shop-domain` header:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <same-valid-hmac-of-body>
   shopify-shop-domain: victim-shop.myshopify.com
   shopify-webhook-id: abc-123
   Body: {"id": 1, "note": "hello"}
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only [1](#0-0)  — validation succeeds because the body is unchanged.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: {...}, ...)` [6](#0-5)  — the host app now processes attacker-controlled data as belonging to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
