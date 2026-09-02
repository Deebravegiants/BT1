### Title
Webhook `shop-domain` header trusted for tenant routing while excluded from HMAC verification enables cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, never the `shop-domain` header, yet `ShopifyAPI::Webhooks::Registry.process` uses that same unauthenticated header value as the tenant identity passed to the app's webhook handler once the body HMAC checks out.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  and `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that body: [2](#0-1) .

`HmacValidator.validate` verifies the HMAC only against `verifiable_query.to_signable_string` (i.e., the body) and `verifiable_query.hmac`: [3](#0-2) .

`Registry.process` gates only on this body-HMAC check, then immediately forwards `request.shop` — the unauthenticated header — to the registered handler as the tenant identity, with no further validation that the header matches the shop that actually produced the signed body: [4](#0-3) .

The broken equality is: **shop authenticated by HMAC (covers only body bytes) ≠ shop used as the tenant key for dispatch (`shopify-shop-domain` header, unauthenticated)**. Any party that can obtain one valid `(body, hmac)` pair signed with the app's `client_secret` — trivially available to an unprivileged attacker who installs the same app on their own store and receives one real webhook — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header (any myshopify domain, including a victim merchant's). The gem's `HmacValidator.validate` will still return `true` because the header is never part of the signed content, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity spoofing primitive delivered entirely through this gem's webhook verification API: an unprivileged actor (one who has only installed the app on their own low-privilege store) can make the host application process a fully "HMAC-verified" webhook under a completely different, arbitrary tenant's identity. Any host application that trusts `WebhookMetadata#shop` (or `request.shop`) as the authenticated tenant — which is exactly what this gem's documented API implies by only requiring `HmacValidator.validate`/`Registry.process` before consuming `request.shop` — will attribute attacker-controlled data/events to a victim shop, corrupting per-tenant state, triggering tenant-scoped side effects (e.g. re-triggering "app/uninstalled" cleanup, GDPR data-request handling, or billing-relevant events) against a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. No secrets are needed beyond obtaining one legitimate `(body, hmac)` pair, which any developer/tester can get by installing the target app on their own store and capturing a single outgoing webhook (e.g. `app/uninstalled` or any low-sensitivity topic). Because the body content for many low-cardinality topics is fixed or attacker-influenceable (e.g., `app/uninstalled` bodies are effectively empty/static across shops), the same signed body/HMAC pair is directly replayable against any target shop by only changing the header, requiring no brute force of the `client_secret`.

### Recommendation
Bind the shop identity into the signed material verified by `HmacValidator`, or independently re-derive/verify the shop from data that is cryptographically bound to the HMAC (e.g., have `Request#to_signable_string` incorporate the `shop-domain` header, or require callers to cross-check `request.shop` against an out-of-band record established during OAuth for a session already known to be legitimate) before dispatching `WebhookMetadata` to handlers. At minimum, document loudly that `request.shop`/`WebhookMetadata#shop` is not authenticated by the HMAC check and must not be treated as a trusted tenant identifier by consuming applications.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers/receives one real webhook, e.g. topic `app/uninstalled` with body `{}` and a valid `x-shopify-hmac-sha256` computed by Shopify with the app's real `client_secret`.
2. Attacker resends that exact `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only (`to_signable_string`) and matches — validation passes: [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: request.shop, ...)` using the attacker-supplied header value `victim-shop.myshopify.com`, and the registered handler executes as if the event genuinely originated from the victim shop: [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
