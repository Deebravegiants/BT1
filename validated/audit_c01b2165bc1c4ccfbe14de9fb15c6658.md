Confirmed: the documentation explicitly says `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "the shop domain of the webhook" — i.e., the gem presents `shop` as an authenticated, trustworthy field derived from the verified request, and downstream apps are told to key their tenant logic off it (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)` in the docs' own example). This confirms the identity-binding break is real and matches the documented API contract, not something requiring the host app to misuse the gem.

### Title
Webhook `shop` (tenant identity) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — read straight from HTTP headers — are never part of the signed payload. `Registry.process` trusts `request.shop` as the authenticated tenant identity and hands it to the app's handler as `WebhookMetadata#shop`, which the gem's own documentation instructs developers to use as the shop for which the webhook applies.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `HmacValidator.validate` computes and compares the HMAC exclusively against `to_signable_string`: [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled from headers that are never mixed into the signed string: [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity, passing it straight into `WebhookMetadata`: [4](#0-3) . The gem's documentation confirms this is the intended trust contract: `Registry.process` is documented to "verify the request did indeed come from Shopify," and `data.shop` is documented as "The shop domain of the webhook," which the example handler uses directly for tenant-scoped work (`shop_domain: data.shop`).

**Broken equality:** `shop_authenticated_by_hmac == shop_acted_upon_by_handler` does not hold. The HMAC only authenticates `raw_body` bytes; `shop_acted_upon = header["shopify-shop-domain"]` is an independent, unauthenticated field.

### Impact Explanation
An attacker who can obtain one valid `(raw_body, hmac)` pair for a webhook topic — e.g. by installing the same app on a store they control and observing genuine Shopify webhook deliveries — can replay that exact body+HMAC to the merchant app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. Because the signature check only covers the body, the forged request passes `HmacValidator.validate` unchanged, and the handler receives `WebhookMetadata` claiming the payload belongs to the victim shop. Any host app that follows the documented pattern (using `data.shop` to select/authenticate the tenant record to update) will process attacker-supplied data under the wrong tenant — a cross-tenant data integrity/confusion issue.

### Likelihood Explanation
Requires only network access to the app's public webhook callback URL and one legitimately-signed webhook (obtainable by running a free/trial store with the same app installed). No `api_secret_key`, access token, or privileged account is needed — this is exploitable by an ordinary unprivileged internet user who can install the target app on their own store.

### Recommendation
Include the tenant-identifying header (`shop-domain`, and ideally `topic`/`webhook-id`) inside the HMAC-signed payload, or otherwise cryptographically bind them to the body (e.g., HMAC over `"#{shop}\n#{topic}\n#{raw_body}"`), so that `to_signable_string` covers every field the handler treats as authenticated before `Registry.process` passes it to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and subscribes to `orders/create` (or any topic the app handles).
2. Shopify delivers a genuine webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `api_secret_key`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the exact `(B, H)` pair to the app's webhook endpoint, but rewrites the `X-Shopify-Shop-Domain` header to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [5](#0-4) .
5. The handler is invoked with `WebhookMetadata(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it originated from `victim.myshopify.com`.

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
