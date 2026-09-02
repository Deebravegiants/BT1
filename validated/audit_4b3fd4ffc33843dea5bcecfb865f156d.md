This confirms the root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are all read directly from unsigned HTTP headers [2](#0-1) . `Registry.process` validates only this body-only HMAC and then passes the header-derived, unauthenticated `shop` value straight to the app's handler as the tenant identifier [3](#0-2) .

### Title
Webhook tenant identity (`shop`) not bound to HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only [1](#0-0) , but `Registry.process` trusts the `shop` (and `topic`/`webhook_id`) values taken from separate, unsigned HTTP headers [4](#0-3)  when constructing `WebhookMetadata` for the app's handler [5](#0-4) .

### Finding Description
`Utils::HmacValidator.validate` recomputes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field using `OpenSSL.secure_compare` [6](#0-5) . For webhook requests, `to_signable_string` is defined as `@raw_body` alone [1](#0-0) . The `shop`, `topic`, and `webhook_id` fields are derived purely from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) that are never part of the signable string [2](#0-1) .

This breaks the identity binding: `HMAC(secret, raw_body) == HMAC(secret, raw_body)` holds true regardless of the `shop` header value, so the equality that should be enforced — "the shop the HMAC authenticates" == "the shop acted on by the handler" — does not hold. `Registry.process` validates the HMAC and then immediately forwards `request.shop` (header-sourced, unauthenticated) as the tenant identifier to the app's webhook handler [5](#0-4) . Any party capable of producing a body+HMAC pair that validates for one shop (e.g., a merchant who has installed the app on a shop they control, and who can capture the resulting webhook request to their own endpoint since HMAC is a documented public verification mechanism computed over body only) can replay that exact body and HMAC while substituting a different value in the `shop-domain` header, causing the handler to attribute the payload to an arbitrary victim shop.

### Impact Explanation
Because `data.shop` from `WebhookMetadata` is typically used by host applications as the tenant key to look up records, update state, or trigger side effects per merchant [7](#0-6) , an attacker who controls one legitimate shop's webhook traffic can inject events falsely attributed to a different shop into the app, without ever needing that shop's access token, `client_secret`, or the app's credentials. This is a cross-tenant data/action injection into another tenant's context, satisfying the "cross-tenant access" impact bar.

### Likelihood Explanation
The attacker only needs to be a legitimate merchant who has installed the app on a shop they control (an "unprivileged internet user" relative to any other tenant) and be able to observe the raw body and HMAC of a webhook Shopify sends to the app for their own shop (e.g. by running their own receiver/tunnel). No secret key, session, or access token belonging to another tenant is required — only manipulation of the plaintext `shop-domain` header on replay, since the header is never covered by the signature.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string for webhook requests (or otherwise cryptographically bind them to the HMAC), so `Utils::HmacValidator.validate` fails if any of these header-derived fields are altered. At minimum, document and encourage host apps to independently confirm the `shop` header value against a known, previously-registered shop for that specific webhook subscription before trusting it as a tenant key.

### Proof of Concept
1. App installs the gem's webhook handling for topic `orders/create` and shop A (`shop-a.myshopify.com`) legitimately installs the app; a real Shopify webhook is delivered to the app's endpoint with body `B`, headers including `x-shopify-shop-domain: shop-a.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over `B`.
2. The attacker (who controls shop A) intercepts/records this legitimate request (headers + body).
3. The attacker resends the identical body `B` and identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but with header `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop).
4. `Utils::HmacValidator.validate(request)` in `Registry.process` still returns `true`, because it only hashes `@raw_body`, which is unchanged [1](#0-0) .
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: ..., ...))`, delivering attacker-controlled data attributed to shop B's tenant context [7](#0-6) .

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
