### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request **body**, then unconditionally trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` **headers** — none of which are part of the signed material — to build the `WebhookMetadata` object that is handed to the app's `WebhookHandler`. This is the same bug class as the reported issue: a value that matters for a security decision (which shop/tenant this data belongs to) is not included in the cryptographic check that is supposed to authenticate the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` then uses `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all sourced from unauthenticated HTTP headers — to build the metadata that is handed to the app's handler for business-logic routing/tenant attribution: [3](#0-2) [4](#0-3) [5](#0-4) 

The binding that should hold is:
`shop asserted in the header == shop that the HMAC actually authenticates`

But the HMAC computation never incorporates `shop`, `topic`, or `webhook_id` at all — `HmacValidator.validate` only proves "this body was signed with `api_secret_key`," a secret that is the **same for every shop that installs the app**, not "this body belongs to shop X." Any party that can obtain one validly-signed `(body, hmac)` pair for the app (e.g., by installing the app on their own store and observing a real webhook delivery) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header. `HmacValidator.validate` will still return `true` because it never looks at those headers, and `Registry.process` will pass the attacker-chosen `shop` straight into `WebhookMetadata`, which host applications use to attribute the event to a specific merchant/tenant.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce: a request that is "authenticated" as coming from the app's Shopify webhook subsystem can be attributed to any shop of the attacker's choosing, not the shop that actually produced the data. Because `shop` is the only tenant-scoping value most host applications key off of when persisting/acting on webhook payloads (as documented in this gem's own usage docs for session/tenant identification), this enables cross-tenant data injection/corruption for any merchant using an app built on this gem — matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only the ability to become a legitimate (even trial) installer of the target app to capture one authentic `(raw_body, x-shopify-hmac-sha256)` pair — no access to `api_secret_key`, access tokens, or any privileged credential is needed, since `api_secret_key` is never exposed by this replay. The attacker then re-sends that untouched body/HMAC pair to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header (and adjusted `x-shopify-topic`/`x-shopify-webhook-id` if desired, which are likewise unauthenticated). `Utils::HmacValidator.validate` performs no cross-check between the header claims and the signed body, so the forged request passes validation deterministically, every time.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable representation used by `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them to the payload), so that `Utils::HmacValidator.validate` proves the full tuple `(shop, topic, webhook_id, body)` was signed together by Shopify, not just the body in isolation. At minimum, document/enforce that host applications must independently verify `request.shop` against known installed-shop records before trusting it for tenant attribution, since the current gem-level check does not provide that guarantee.

### Proof of Concept
1. Attacker installs the victim app on their own development store `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` sent to the app's webhook endpoint.
2. Attacker replays the exact same `B` to the app's webhook endpoint, but sets:
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only signs `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` (forged/reused arbitrarily)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (= `B`) and finds it matches `H`, so validation succeeds: [6](#0-5) 
4. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though the payload `B` actually originated from the attacker's own shop, letting the attacker inject arbitrary webhook data attributed to the victim tenant.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
