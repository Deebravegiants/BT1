## Analysis

The reported bug class ("value used by downstream logic is not the value that was cryptographically verified") maps directly onto how this gem validates inbound Shopify webhooks.

### Root cause

`ShopifyAPI::Webhooks::Request` implements the `VerifiableQuery` interface consumed by `HmacValidator`. Its `to_signable_string` — the only data fed into the HMAC computation — is just the raw body: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers, completely outside the signed material: [2](#0-1) 

`HmacValidator.validate` only proves that `raw_body` was signed with the app's `api_secret_key`; it says nothing about which shop or topic that body belongs to: [3](#0-2) 

`Registry.process` then trusts these unauthenticated header values and forwards them to the app's handler as if they were verified: [4](#0-3) 

The identity binding that should hold is:
`HMAC-verified(shop, topic, webhook_id, body) == (shop, topic, webhook_id, body) delivered to handler`

What actually holds is only:
`HMAC-verified(body) == body delivered to handler`, while `(shop, topic, webhook_id)` are unauthenticated.

### Why this is exploitable across tenants

Shopify signs webhooks using the app's single, app-wide `client_secret` — the same key regardless of which merchant triggered the event. Any unprivileged internet user can become a legitimate (if low-privilege) merchant by installing the app on their own store, which lets them receive genuinely-signed webhooks for their own shop. Because the signature covers only `raw_body`, that attacker can replay a captured, validly-signed webhook payload to the app's webhook endpoint while swapping `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` to any value — including another tenant's shop domain — and `HmacValidator.validate` still returns `true`. The app's handler (per the documented usage pattern) uses `WebhookMetadata#shop` to decide which tenant's record to update, so this breaks the shop-to-signature binding and allows cross-tenant data injection/impersonation.

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `HmacValidator.validate` proves nothing about the `shop`, `topic`, or `webhook_id` values that `Registry.process` later trusts and hands to the app's webhook handler.

### Finding Description
`Request#hmac` is derived from the `hmac-sha256` header and validated against `to_signable_string`, which is hard-coded to `@raw_body` ( [1](#0-0) ). Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are parsed from separate, unsigned headers ( [5](#0-4) ). `Registry.process` checks only `HmacValidator.validate(request)` and then dispatches `request.shop`/`request.topic`/`request.webhook_id` unchanged to the registered handler ( [4](#0-3) ). Since Shopify signs webhooks with the app's single shared `client_secret` (not a per-shop key), any merchant who installs the app can obtain a validly-signed payload for their own shop and then re-submit it to the app's webhook endpoint with the `shop`, `topic`, or `webhook_id` headers altered — the signature still verifies because those fields were never part of the signed material.

### Impact Explanation
This breaks the tenant-identity binding the host application relies on: a webhook that passes HMAC validation is assumed by convention to genuinely originate from, and describe, the shop named in `x-shopify-shop-domain`. An attacker-controlled shop identifier let through unauthenticated allows cross-tenant impersonation — the app can be made to process attacker-supplied (but validly-HMAC'd) data as an event belonging to a different merchant, corrupting that merchant's records or triggering shop-scoped side effects (e.g., mandatory compliance topics like `customers/redact`) under a forged tenant identity.

### Likelihood Explanation
Any user can install the target app on their own store to legitimately receive an HMAC-signed webhook, then replay the exact same signed body against the endpoint while modifying the `shop-domain`/`topic`/`webhook-id` headers, which requires no secret knowledge beyond capturing their own traffic (e.g., via a proxy). No `api_secret_key`, access token, or privileged access is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed payload used for HMAC verification (or otherwise cryptographically bind them to the body), so that `HmacValidator.validate` fails if any of these header values are altered independently of the signed body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the raw request Shopify sends to the app, including the valid `x-shopify-hmac-sha256` header (computed over `raw_body` with the app's shared `client_secret`).
3. Attacker resends the identical `raw_body` and `hmac-sha256` header to the same webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`).
4. `HmacValidator.validate` in [3](#0-2)  returns `true` because it only checks `raw_body` against the signature.
5. `Registry.process` ( [4](#0-3) ) invokes the registered handler with `shop: "victim.myshopify.com"`, causing the app to process attacker-controlled data under the victim shop's identity.

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
