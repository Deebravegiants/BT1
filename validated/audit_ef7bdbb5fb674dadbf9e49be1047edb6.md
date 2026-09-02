### Title
Webhook `shop` (and `topic`) identity is taken from unauthenticated HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. This breaks the binding "shop authenticated == shop the payload is attributed to," letting a party that legitimately receives one authentic webhook (for their own shop) replay its (body, hmac) pair with a different `shop-domain` header to make the app process data attributed to another tenant.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC solely over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw body, never the headers: [2](#0-1) 

Yet `shop`, `topic`, `webhook_id`, and `api_version` — the values used to route and attribute the webhook to a specific merchant — are read directly, unauthenticated, from HTTP headers: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body's authenticity) and then dispatches the handler using the unauthenticated `request.shop`/`request.topic`: [4](#0-3) 

This is the direct analog of the reported bug class: a field (`pricesWereSafe`/here, the tenant `shop`) that is produced by a check (`isSpotSafe`/here, HMAC validity) but a *different*, unchecked field (the actual price used/here, the `shop` header) is the one the caller actually acts on. The equality that should hold is:
`shop authenticated by the HMAC == shop attributed to the webhook data`
but in fact the HMAC only proves `body authenticated by the HMAC == body received`; the `shop` header is disjoint from what the signature covers.

Since Shopify signs webhooks using the app's `client_secret`, which is identical for every shop that installs the app, any merchant who legitimately installs the app receives real webhooks for their own store with a valid HMAC over their own body. That merchant can capture a `(raw_body, hmac)` pair from their own legitimate webhook traffic and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still passes (it only checks the body), but `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop: [5](#0-4) 

Any host application that uses `data.shop` to select the session/access token or to record/act on tenant-scoped state (which is the documented purpose of this field) will process attacker-supplied data under a foreign tenant's identity.

### Impact Explanation
This crosses a tenant boundary using only credentials any unprivileged user can obtain by installing the app on their own store (no `api_secret_key`, no stolen access token, no privileged account needed) — cross-tenant access, matching the Critical impact bucket for this scan.

### Likelihood Explanation
Any developer/attacker can install the target app on a free/trial Shopify store, capture one legitimate webhook body+HMAC for a topic of interest (e.g. `customers/redact`, `orders/create`, `app/uninstalled`), and replay it against the shared webhook endpoint with a forged `x-shopify-shop-domain` header. No secret material or interaction with the victim is required, only knowledge of the target shop's domain (public information) and the app's single shared webhook endpoint URL. This is straightforward and repeatable.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) header values into the signed material, or otherwise cryptographically tie the header-derived shop to session/installation state before it is trusted (e.g., verify the `shop` header corresponds to an active, previously-recorded installation session, or require the host app to cross-check `data.shop` against its own tenant records rather than trusting it implicitly). At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated and must not be used as the sole tenant-identity signal by consuming applications, and add a way for `Registry.process` to enforce shop/topic binding to the verified payload.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, becoming a legitimate merchant.
2. Shopify sends a genuine webhook to the app's endpoint:
   - headers: `x-shopify-topic: customers/redact`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over body>`
   - body: `{"customer": {...}, "shop_id": ...}`
3. Attacker captures the raw body and the valid `hmac` header (both are visible to them as the receiving party, or they capture it via their own logging middleware).
4. Attacker resends the identical body and `hmac` header to the app's webhook endpoint, replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (unchanged) hmac: [6](#0-5) 
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, and any host-application logic keyed on `data.shop` (e.g. session lookup, redaction, order processing) executes under the victim tenant's identity using attacker-supplied data.

### Citations

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
