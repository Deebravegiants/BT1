## Title
Webhook Shop/Topic/Metadata Headers Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body via HMAC, while the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — are used unchanged by `ShopifyAPI::Webhooks::Registry.process` to build the `WebhookMetadata` that gets handed to the app's webhook handler. Because a single app-level `client_secret` signs webhooks for *every* shop that installs the app, any party that can obtain one validly-signed webhook body (e.g. from a shop they control/trial-install) can replay that exact body while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain, producing a signature that still validates while the tenant identity is forged.

### Finding Description
`Request#hmac` and `Request#to_signable_string` bind the HMAC exclusively to `@raw_body`: [1](#0-0) [2](#0-1) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from headers that are never included in the signable string: [3](#0-2) 

`HmacValidator.validate` only checks the body-derived signature: [4](#0-3) 

`Registry.process` trusts `request.shop` (and the other header-derived fields) as the tenant identity handed to the app's handler, with no additional binding check between the verified body and the claimed shop: [5](#0-4) 

The equality this breaks is: **shop the HMAC actually authenticates (none — HMAC only authenticates body bytes) vs. shop used as the tenant key passed to `WebhookMetadata`/the app handler** (`request.shop`, an unauthenticated header value). Since `Context.api_secret_key` is one shared secret for the whole app across all its installed shops, a signature computed over a given body is valid regardless of which shop it is replayed against — the header claiming the shop is never part of what's signed.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who controls one shop that has installed the target app (e.g., a free dev-store install, satisfying no special privilege beyond "unprivileged internet user with respect to other tenants") can capture a legitimately-signed webhook payload from their own shop, then resend the same raw body to the app's webhook endpoint with `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) rewritten to reference a different, victim shop. `Utils::HmacValidator.validate` still returns `true` because it only re-derives the HMAC from `@raw_body`, and `Registry.process` dispatches to the handler with `shop: request.shop` set to the attacker-chosen victim domain. Any host application that keys its persistence, side effects, or session lookups by `WebhookMetadata#shop` (as the gem's own docs pattern of `data.shop` implies) will attribute the forged/replayed payload to the wrong tenant, enabling cross-tenant data confusion/injection into another merchant's app state.

### Likelihood Explanation
The prerequisite is modest: the attacker needs only one instance where the app is installed on a shop they control, and the ability to capture and replay one signed webhook body to the app's public webhook endpoint with a modified `X-Shopify-Shop-Domain` header — no access to `api_secret_key`, no privileged account on the victim shop, and no TLS interception is required.

### Recommendation
Include the `shop`, `topic`, and `webhook_id`/`api_version` values in the signable material (or otherwise cryptographically bind them, e.g. by validating them against an expected/registered shop before dispatch) so that `HmacValidator.validate` fails if any of these header-derived fields are altered relative to what was actually signed by Shopify for that specific delivery.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook delivery, e.g. body `{}` with headers `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Replay the identical raw body and HMAC header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the unchanged HMAC (`lib/shopify_api/webhooks/request.rb:10-13,35-38`; `lib/shopify_api/utils/hmac_validator.rb:12-22`).
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", ...))` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to process an attacker-crafted payload under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
