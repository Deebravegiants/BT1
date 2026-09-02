### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `shopify-shop-domain` HTTP header, but the HMAC signature verified by `Utils::HmacValidator.validate` only covers the raw request body. Because the app's HMAC secret (`Context.api_secret_key`) is shared across every shop that has the app installed, anyone who can trigger a legitimately-signed webhook for their *own* shop (e.g., a free/dev store) can capture a valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with a forged `shopify-shop-domain` header pointing at a victim shop. `Registry.process` will accept the HMAC as valid and dispatch the handler with the attacker-chosen `shop`, breaking the binding `shop authenticated == shop the signature actually vouches for`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from attacker-controllable HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)`, i.e. only that the body's HMAC matches — it performs no check that the `shop` header matches the shop the signature was actually generated for, and then hands the raw header-derived `shop` value straight to the handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signature is computed only from `verifiable_query.to_signable_string` (the body) using the single, app-wide `Context.api_secret_key`: [4](#0-3) 

Because Shopify's webhook HMAC secret is per-app, not per-shop, a valid `(body, hmac)` pair generated for shop A's webhook remains a valid HMAC pair regardless of which `shop-domain` header accompanies it — the header is never part of the signed content. This is the same class of bug as the reported "field acted on but not covered by the signature" issue: the binding `verified-signature-owner == identity field the code trusts` does not hold.

### Impact Explanation
Any unprivileged internet user who can install the app on a shop they control (including a free Shopify development/trial store) can:
1. Trigger any webhook topic for their own shop to obtain a valid `raw_body` + `hmac-sha256` pair signed with the shared `Context.api_secret_key`.
2. Replay that exact body/HMAC to the app's public webhook endpoint, substituting the `shopify-shop-domain` header (and, if desired, `shopify-topic`/`shopify-webhook-id`) with an arbitrary victim shop's domain.
3. `Registry.process` will accept the HMAC as valid (it only checks the body) and invoke the registered handler with `WebhookMetadata` carrying the attacker-chosen `shop`, `topic`, and `webhook_id`.

This lets an attacker inject fabricated webhook events attributed to a victim tenant into any host application that trusts `request.shop`/`WebhookMetadata#shop` for tenant-scoped data writes (e.g., `orders/create`, `app/uninstalled`, `customers/data_request`), enabling cross-tenant data corruption or triggering tenant-scoped business logic (uninstall flows, GDPR redaction, order processing) for a shop the attacker does not own. This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Likelihood is high in any deployment where the host application relies solely on `ShopifyAPI::Webhooks::Registry.process`/`Utils::HmacValidator.validate` for both authenticity and tenant-attribution: no additional secret, token, or privileged access is required — only the ability to install the app on any shop (including a free dev store) and send an HTTP request with attacker-controlled headers to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and `topic`/`webhook_id`) values into the material that is verified against the HMAC, or independently verify that the `shop-domain` header corresponds to a shop with a currently valid installation/session before trusting it, rather than trusting raw headers once the body-only HMAC check passes. At minimum, document that `Registry.process` is not tenant-safe and host applications must independently confirm the shop is one they have an active session for before acting on the webhook payload.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker-shop.myshopify.com` and trigger any subscribed webhook topic (e.g. `orders/create`) to receive a legitimately signed callback with body `B` and header `x-shopify-hmac-sha256: H` (valid against the app's single `api_secret_key`).
2. Replay a forged HTTP POST to the app's webhook route with the same raw body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` builds the request; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `@raw_body` (unchanged).
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, i.e. the app now processes attacker-supplied data as if it originated from the victim shop, as shown in [3](#0-2) .

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
