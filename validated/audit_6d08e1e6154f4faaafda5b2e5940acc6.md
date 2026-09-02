## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is taken from unauthenticated headers while the HMAC only signs the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` by reading them straight out of HTTP headers, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates only covers the raw request body. Nothing binds the header-derived `shop` (the tenant identifier delivered to the app's handler) to the value that was actually signed by Shopify.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header: [2](#0-1) 

but `Request#shop`, `#topic`, and `#webhook_id` are pulled directly from unauthenticated headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`) that are never part of the signed content: [3](#0-2) 

`Registry.process` validates only the body/HMAC pair and then hands the header-derived, unauthenticated `shop`/`topic`/`webhook_id` straight to the app's handler as `WebhookMetadata`: [4](#0-3) 

The identity binding that should hold is: `shop_used_by_handler == shop_that_the_signed_payload_actually_originated_from`. Because the HMAC secret (`Context.api_secret_key`) is per-app, not per-shop, and the signature covers only the byte content of the body, any two webhook deliveries to the same app that share identical `raw_body` bytes will carry identical valid HMACs regardless of which shop they came from. An attacker who controls a shop with the app installed can capture a legitimately-signed `(raw_body, hmac)` pair from their own store, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds (it never inspects the shop header), so the forged request is accepted and dispatched to the handler tagged with the victim's shop.

This mirrors the reported bug class: a field that downstream logic acts on (`payee` in the original report; here, `shop`/`topic` used to key tenant-scoped webhook handling) is never re-synchronized with/covered by the authenticating check (`y-intercept`/`slope` there; the HMAC signature here).

### Impact Explanation
Apps commonly key persistent, tenant-scoped side effects directly off `WebhookMetadata#shop` — e.g. deleting/clearing shop data on `app/uninstalled`, disabling billing, revoking sessions, or writing shop-scoped records. Because `shop` is unauthenticated relative to the signature, a malicious merchant/attacker who has installed the app on their own store can forge webhook deliveries that are processed as if they originated from an arbitrary victim shop, achieving cross-tenant state manipulation without ever possessing the victim's access token or credentials. This satisfies the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Exploitation requires only: (1) installing the app on an attacker-controlled shop to legitimately receive a webhook and capture its `(raw_body, hmac)` pair, and (2) replaying that exact byte-for-byte body with a spoofed `shop-domain`/`topic` header to the app's public webhook endpoint. No access token, secret, or privileged access to the victim is required — only knowledge of the victim's `myshopify.com` domain, which is typically public. This is reachable by any unprivileged internet user who can install the app once.

### Recommendation
Bind the header-derived identity to the signed payload. Include `shop`, `topic`, and `webhook_id` in the HMAC-signable content (as Shopify's own webhook signing effectively assumes via delivery to a shop-registered, per-registration callback URL), or otherwise cryptographically verify that the claimed `shop` matches a shop known to have this webhook/topic registered before dispatching to handlers. At minimum, document and enforce that `to_signable_string` must cover all fields consumed from `WebhookMetadata`, not just the raw body.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`.
2. Trigger a webhook event (e.g., `app/uninstalled`) and capture the raw POST body and its `x-shopify-hmac-sha256` header — this HMAC is valid because it's computed only over the body using the app's shared secret.
3. Replay the exact same body and `hmac` header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` in `HmacValidator#validate_signature` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `raw_body` against the secret.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to perform shop-scoped actions (e.g., data deletion) against the victim tenant.

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
