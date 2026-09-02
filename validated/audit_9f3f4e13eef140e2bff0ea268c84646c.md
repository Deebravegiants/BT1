### Title
Webhook Identity Headers (`shop`, `topic`, `webhook_id`) Are Not Bound to the HMAC Signature, Enabling Cross-Shop Webhook Replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop, topic, and webhook-id identity for a webhook exclusively from unauthenticated HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body. This breaks the identity binding `shop-domain header == shop bound by the HMAC`, allowing an attacker who has captured one legitimately-signed webhook body (e.g., a webhook delivered to their own installed shop) to replay that exact body/HMAC pair while substituting a different `shop-domain` (and `topic`/`webhook-id`) header, and have it accepted as authentic for another merchant's shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but the identity fields consumed downstream — `shop`, `topic`, and `webhook_id` — are read straight from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` trusts this validation result and then forwards the (unauthenticated) `request.shop`, `request.topic`, and `request.webhook_id` straight to the app's handler: [4](#0-3) 

Equality that should hold: `shop bound by HMAC == shop the handler acts on`. In practice: `HMAC covers raw_body only`, while `handler acts on header-derived shop/topic/webhook_id`, so the two are never actually equal — the shop identity is never authenticated, only the body bytes are.

### Impact Explanation
Any entity that can install the app on a shop they control (an unprivileged internet user, from the app's perspective) receives legitimately Shopify-signed webhook deliveries for that shop — a valid `(raw_body, hmac)` pair requiring no knowledge of `api_secret_key`. Because the header values are outside the signed payload, that same `(raw_body, hmac)` pair remains valid if replayed with a different `shop-domain` header. This lets the attacker impersonate arbitrary victim shops toward the app's webhook handler, causing the app to process attacker-supplied webhook data as if it originated from a different (victim) tenant — a cross-tenant data/authorization confusion inside the app logic that consumes `WebhookMetadata#shop`.

### Likelihood Explanation
Exploitation requires only: (1) installing the app once on an attacker-controlled shop to obtain one authentic `(raw_body, hmac)` webhook delivery, and (2) sending a crafted HTTP POST to the app's webhook endpoint with the captured body/HMAC but altered `shop-domain`/`topic`/`webhook-id` headers. No secret keys, tokens, or privileged access are needed, making this reachable by any unprivileged internet user with a normal app install.

### Recommendation
Include the shop domain, topic, and webhook id in the value that is HMAC-verified (or otherwise cryptographically bind them, e.g. by deriving/validating the shop against a value obtained from an already-authenticated store, such as the session associated with the original OAuth install), instead of trusting `X-Shopify-Shop-Domain`/`X-Shopify-Topic`/`X-Shopify-Webhook-Id` headers as unauthenticated identity data. At minimum, document that consuming applications must independently verify `request.shop` against a known-installed shop before acting on webhook data, and reject webhooks whose shop is not already an authenticated tenant.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because Shopify computed `H = HMAC(secret, B)`).
2. Send a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == H`, per `lib/shopify_api/webhooks/request.rb#L35-L38` and `lib/shopify_api/utils/hmac_validator.rb#L26-L31`.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: "victim-controlled", shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, per `lib/shopify_api/webhooks/registry.rb#L198-L199`, causing the app to act on attacker data under the victim shop's identity.

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
