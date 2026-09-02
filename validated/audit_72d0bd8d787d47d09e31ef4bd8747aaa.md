This confirms the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` (in `lib/shopify_api/utils/hmac_validator.rb`) only checks that signature against `to_signable_string`. The `shop`, `topic`, `webhook_id`, and `api_version` values are all read directly from headers and are never part of the HMAC-signed material.This confirms `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by the HMAC — and forwards them directly into `WebhookMetadata` given to the host app's handler, which uses `shop`/`topic` to route tenant-specific actions (e.g., data deletion, session/store lookups) without any independent verification.

### Title
Webhook HMAC only covers the request body, not the shop/topic/webhook-id headers, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against that body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values, which are read straight from attacker-controllable HTTP headers, are never included in the signed material, yet `ShopifyAPI::Webhooks::Registry.process` trusts them to route the webhook and to populate `WebhookMetadata#shop`/`#topic` handed to the host application's handler.

### Finding Description
The equality the gem is supposed to guarantee is: `shop attested by valid HMAC == shop the handler acts on`. Instead:
- `to_signable_string` in [1](#0-0)  signs only `@raw_body`.
- `HmacValidator.validate_signature` in [2](#0-1)  compares the received HMAC against that body-only signable string using the app's `api_secret_key`.
- `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers with no cryptographic binding: [3](#0-2) .
- `Registry.process` validates the HMAC, then immediately trusts `request.topic`, `request.shop`, and `request.webhook_id` to dispatch the handler and build metadata: [4](#0-3) .

Because a valid HMAC only proves "this body was signed by Shopify with our secret", not "this body was signed for shop X on topic Y", any legitimate webhook body+HMAC pair (which a merchant/attacker who has installed the app on their own store genuinely receives, since Shopify signs webhooks per-app not per-header) can be replayed to the app's webhook endpoint with a different `shop-domain`/`topic`/`webhook-id` header. The signature still validates because those header values were never part of the signed content, so the host application processes the request as if it came from a different tenant.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: `shop` authenticated (implicitly, via a valid signature) is not the same as `shop` the code actually acts on. An attacker who legitimately installs the app on their own shop can capture genuinely-signed webhook bodies (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`) and replay them against the same endpoint while spoofing the `shop-domain` header to point at a victim shop, causing the host app's handler to execute tenant-specific side effects (data deletion/redaction, session invalidation, etc.) attributed to the wrong shop. This qualifies as cross-tenant access under the Critical severity bucket.

### Likelihood Explanation
Likelihood is moderate to high in practice: any entity that installs the app (an "unprivileged internet user" from the app's perspective, since app installation is typically open) receives genuinely HMAC-signed webhooks for their own shop, and only needs to modify unauthenticated headers and resend the same body to the shared webhook endpoint. No access to `api_secret_key`, TLS interception, or privileged credentials is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop` and `topic`) in the signed material `to_signable_string` returns, or otherwise cryptographically bind these header values to the signed body before trusting them in `Registry.process`. Shopify's actual HMAC scheme signs the raw body; the fix should instead be to independently verify `shop`/`topic` against a source of truth (e.g., cross-check against active app installations) before dispatching handlers, rather than trusting header values outright.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering a genuine webhook delivery for topic `app/uninstalled` with body `B` and a valid `X-Shopify-Hmac-Sha256` header computed over `B` using the app's `api_secret_key`.
2. Attacker captures this request (they are the recipient, no interception needed).
3. Attacker resends the identical body `B` and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers normally, `HmacValidator.validate` succeeds (body/HMAC unchanged), and `Registry.process` calls the registered `app/uninstalled` handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`.
5. The host application executes uninstall/redaction logic against `victim-shop.myshopify.com`, a shop the attacker never controls or was authenticated for.

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
