Confirmed: `Utils::VerifiableQuery#to_signable_string` is the only material the HMAC covers, and `Webhooks::Request#to_signable_string` returns just `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC of the body and then dispatches using `request.shop` and `request.topic` as trusted identity fields [3](#0-2) .

### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw HTTP body via `Utils::HmacValidator.validate` [4](#0-3) . That HMAC is computed over `Request#to_signable_string`, which is defined as `@raw_body` only [1](#0-0) . The `shop` (from the `shop-domain` header), `topic`, `webhook_id`, and `api_version` fields are read directly from attacker-controllable HTTP headers and are never included in the signed material [2](#0-1) . Yet `Registry.process` treats `request.shop` as the authenticated tenant identity and forwards it unchanged into `WebhookMetadata`, which host applications use to attribute the webhook payload to a specific merchant/session [5](#0-4) .

### Finding Description
The equality this gem is supposed to enforce is:
`bytes_verified_by_HMAC == bytes_the_application_trusts_as_the_tenant_identity`

In practice the gem enforces only `HMAC(raw_body) == received_hmac`, while the tenant identity (`shop`) and event routing key (`topic`) are taken from separate, unsigned headers. Because Shopify webhook HMACs are computed with the single app-wide `client_secret` — not a per-shop secret — any merchant who installs the app on their own store can trigger a webhook, capture a fully valid `(raw_body, hmac)` pair for their own shop, and then replay that exact body/HMAC pair directly to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header value. `Utils::HmacValidator.validate` only recomputes the HMAC of the body and compares it with `OpenSSL.secure_compare` [6](#0-5) ; it has no way to detect that the shop header has been swapped, so the check passes. `Registry.process` then hands the forged shop identity straight to the registered handler [7](#0-6) .

### Impact Explanation
A host application that uses `WebhookMetadata#shop` to look up merchant-specific session/state (a documented, intended use of this field) would apply another tenant's webhook payload under an attacker-chosen shop identity. This crosses a tenant boundary using only the attacker's own legitimately-issued webhook as raw material — no `api_secret_key`, access token, or privileged account is required. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any merchant who installs the app (an unprivileged action available to any internet user via a free/dev store) can obtain a genuine `(body, hmac)` pair for a topic of their choosing, then send it directly to the app's public webhook endpoint with a modified `shop-domain` header. This requires no MITM, no secret material beyond what Shopify already discloses to any installer via its own webhook delivery, and no interaction with the honest merchant being impersonated.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the signed material, or otherwise authenticate them independently of the body HMAC — e.g., have `to_signable_string` include the canonicalized header values that are trusted downstream, or require the caller to independently verify that the `shop-domain` header matches a shop associated with the topic/registration before invoking the handler.

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com` and subscribes to a webhook topic the app handles (e.g. `orders/create`).
2. Attacker triggers the event and captures the genuine request Shopify sends to the app's webhook endpoint, including the raw body and the `x-shopify-hmac-sha256` header (a valid HMAC over that body, keyed with the app's shared `client_secret`).
3. Attacker crafts a new HTTP POST to the same public webhook endpoint, using the identical body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over the (unchanged) body and it matches, so `Registry.process` proceeds and calls the handler with `shop: "victim.myshopify.com"` [5](#0-4) , even though the payload actually originated from the attacker's own store.

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
