Confirmed. The `Webhooks::Request` class binds only the raw body to the HMAC, while the tenant identity (`shop`), `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers and never bound into the signature.### Title
Webhook shop-tenant identity is not covered by the HMAC signature, enabling cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable HMAC signature over the raw request body only, while `shop`, `topic`, and `webhook_id` — the values used to attribute a webhook event to a specific merchant tenant and dispatch it to a handler — are read straight from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop`, `#topic`, and `#webhook_id` are parsed directly from the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers, with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which calls `to_signable_string` (body only) — and then, having only proven the *body* bytes are legitimately signed, trusts the header-derived `shop`, `topic`, and `webhook_id` to construct the dispatched `WebhookMetadata` and select the handler: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the HMAC purely from `verifiable_query.to_signable_string`: [4](#0-3) 

This breaks the identity binding: **HMAC-verified bytes (body) ≠ bytes trusted for tenant/routing identity (shop, topic, webhook_id headers)**. An attacker who can capture one legitimate webhook delivery (body + valid HMAC) for any shop that has the app installed — e.g., their own store, since app installation is open to any merchant — can resend that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain, or the `x-shopify-topic`/`x-shopify-webhook-id` headers with different values. `Utils::HmacValidator.validate` will still return `true` because it only checks the body, and `Registry.process` will hand the host application a `WebhookMetadata` claiming the (forged) shop and topic, with data actually belonging to a different tenant/event.

### Impact Explanation
This directly matches the "Critical - cross-tenant access" category: the gem's own HMAC verification API gives host applications a false assurance that `shop`/`topic`/`webhook_id` are authenticated when they are not. Applications that rely on `WebhookMetadata#shop` (as returned by this gem, per its documented `Registry.process` contract) to key data writes, session lookups, or GDPR/redaction routing per merchant can have another tenant's legitimate payload attributed to, and processed under, an arbitrary shop domain, or have an event replayed under a different topic than what was actually signed.

### Likelihood Explanation
Moderate-to-high: the attacker needs one genuine webhook delivery with a valid HMAC (trivially obtainable by installing the app on the attacker's own store, a normal unprivileged action) and does not need the `api_secret_key`. No privileged access, TLS interception, or credential theft is required — only crafting an HTTP POST with modified headers and the same body/HMAC pair.

### Recommendation
Include the identity-relevant fields (`shop`, `topic`, `webhook_id`, `api-version`) in the signed/verifiable material, or otherwise cryptographically bind them to the request (e.g., derive `to_signable_string` from a canonicalized combination of headers + body, matching what Shopify actually includes when generating the signature), so `HmacValidator.validate` fails whenever any of these attacker-controllable header values is altered relative to what was actually signed by Shopify.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-webhook-id: W`.
2. Replay the request to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — see: [1](#0-0) 
It returns `true` since `B` and `H` still match.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged `shop` header and dispatches it to the handler registered for that topic, as shown at: [5](#0-4) 
The host application now processes attacker-supplied data as an authenticated webhook for `victim.myshopify.com`.

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
