### Title
Webhook `shop-domain` header is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then dispatches to the handler using the header-derived `shop` value without any cryptographic binding between that value and the signed payload.

### Finding Description
`Request#to_signable_string` is defined as simply the raw body bytes: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` — the fields that determine *which tenant* and *which event* the webhook represents — are pulled straight from HTTP headers with no HMAC coverage: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only, using the app's single shared `api_secret_key`) and then trusts the header-derived `shop`/`topic` to build `WebhookMetadata`, which the host app uses to attribute the event to a tenant: [3](#0-2) 

`HmacValidator.validate` proves only that "the body was signed with this app's secret" — it says nothing about which shop or topic the signer intended: [4](#0-3) 

The equality this gem's `process` should guarantee is:
`shop_authenticated_by_signature == shop_acted_upon_by_handler`

But since `shop` (and `topic`/`webhook_id`) are outside the signable string, that equality never holds — any bytes with a valid signature for *some* legitimate webhook body can be replayed with an arbitrary `x-shopify-shop-domain` / `x-shopify-topic` header and will pass `process` unmodified.

Because `api_secret_key` is shared across every shop that has installed the app, an unprivileged party who is merely one legitimate (even free/trial) tenant of the app can capture a real webhook delivery they legitimately receive (valid `raw_body` + valid `hmac`), and replay that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop and/or a `topic` header matching a handler that only inspects fields present in that shared body shape. `Registry.process` will accept it as authentic for the victim shop, since nothing ties the signature to the header values.

### Impact Explanation
This breaks the tenant isolation boundary the gem is supposed to provide: an attacker-controlled shop can forge webhook events attributed to a different merchant's shop, causing the host application to process/act on data (e.g. order, app-uninstall, GDPR, fulfillment webhooks) under the wrong tenant's identity. This is a cross-tenant confusion vulnerability stemming entirely from this gem's webhook verification logic (`Utils::HmacValidator` + `Webhooks::Request`/`Registry`), not from host-application misuse — the gem's own API contract (`process`) leads callers to trust `shop`/`topic` as authenticated once `process` succeeds, when in fact only the body bytes are authenticated.

### Likelihood Explanation
Low-to-moderate: exploitation requires (1) the attacker to be, or transiently register as, an installed shop of the same app (to receive at least one real, validly-signed webhook body), and (2) knowledge of the app's public webhook endpoint URL (typically discoverable/config'd per app). No access to `api_secret_key`, tokens, or TLS interception is required — only replay of previously-received, legitimately-signed bytes with attacker-chosen headers.

### Recommendation
Bind the identity-relevant headers (`shop`, `topic`, `webhook-id`, `api-version`) into the signable string used for HMAC verification, or otherwise cryptographically tie them to the signed payload, so `Utils::HmacValidator.validate` proves authenticity of the *(shop, topic, body)* tuple rather than the body alone. At minimum, document and enforce that host apps cannot trust `WebhookMetadata#shop`/`#topic` as tenant-authenticated unless cross-checked against an independently verified session/shop record.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, low-privilege install).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker captures `raw_body` and the `hmac` value (both are delivered to them as the shop owner, not secret).
4. Attacker replays a new POST to the same endpoint with the identical `raw_body`/`hmac`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` (the body) and its hmac are unchanged.
6. The registered handler for `orders/create` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to process the forged event as belonging to `victim-shop.myshopify.com`.

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
