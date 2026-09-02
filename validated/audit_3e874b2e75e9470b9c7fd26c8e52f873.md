### Title
Webhook `shop-domain` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor (from the `X-Shopify-Shop-Domain` header) that `ShopifyAPI::Webhooks::Registry.process` hands to app-provided webhook handlers via `WebhookMetadata.shop` as the authenticated tenant identity for the event. However, the HMAC that `Registry.process` verifies via `Utils::HmacValidator.validate` is computed only over the raw request body, never over the shop header. This breaks the intended equality `shop header used by the handler == shop actually authenticated by the HMAC`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is completely independent of the signed bytes: [2](#0-1) 

`Registry.process` verifies the HMAC (body-only) and then trusts `request.shop` to build the metadata passed to the handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the digest strictly against `verifiable_query.to_signable_string`, i.e., the raw body only: [4](#0-3) 

Because a single app has one shared `api_secret_key` used to sign webhooks for *every* installed shop (not a per-shop secret), any unprivileged internet user who installs the public app on their own shop can legitimately receive webhook deliveries with a valid HMAC computed over a body they fully control (e.g., by updating a resource on their own store to trigger `products/update`, `orders/create`, etc.). The attacker can then replay that exact `(raw_body, hmac-sha256)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still passes (it only checks the body against the shared secret), and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the victim's domain even though the payload actually originated from the attacker's own shop.

This matches the requested analog class: "a shop authenticated versus the shop stored as a session key" — the gem authenticates only the body, but hands callers a `shop` value that is asserted, not authenticated, and this `shop` is exactly the value host applications are expected to use to key their tenant/session storage (see `docs`/`BREAKING_CHANGES_FOR_V16.md` reference implementation, which keys session storage by `shop`).

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (as documented/intended) to select which merchant's data record to create/update/delete in response to a webhook, an attacker who has merely installed the app on their own store can forge a webhook that appears to originate from a completely different shop. This is a cross-tenant access/data-integrity issue: an unprivileged, unrelated party (having no relationship with the victim shop) can inject or corrupt data attributed to the victim tenant purely by controlling the `shop-domain` header while replaying/self-generating a validly-HMAC'd body from their own install. This satisfies the "cross-tenant access" Critical-impact category, since no credential of the target shop or the app's `client_secret` is required — only a legitimate install of the app by the attacker on their own tenant plus control over HTTP headers sent to the app's public webhook endpoint.

### Likelihood Explanation
Likelihood is high for any app that (a) is installed by more than one merchant (multi-tenant SaaS, the typical Shopify app deployment model) and (b) uses the gem's documented `Webhooks::Registry`/`WebhookMetadata#shop` value to scope handler logic to a shop record — which is the expected/only way this gem exposes shop identity to webhook handlers. The attack requires no secrets beyond what any merchant installing the app already has (their own legitimate webhook deliveries), and crafting/replaying an HTTP request with a spoofed header is trivial.

### Recommendation
Bind the shop identity to the HMAC-verified data instead of trusting an unauthenticated header:
- Prefer deriving/confirming shop identity from a value that Shopify includes inside the authenticated payload where applicable, or
- Require host applications to independently corroborate `request.shop` against a shop already known to be associated with that specific webhook subscription/handler (e.g., via a per-shop webhook secret or a stored mapping of webhook id → shop) rather than trusting the header value verbatim, and
- Document clearly (and ideally enforce in `Webhooks::Registry.process`) that `shop` from `Webhooks::Request` is unauthenticated and must not be used alone to select which tenant's data to mutate without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` (fully permitted, ordinary merchant action).
2. Attacker triggers or waits for a webhook delivery for a topic handled by the app (e.g. `products/update`), capturing the raw POST body and the resulting `X-Shopify-Hmac-Sha256` header — both computed by Shopify using the app's single shared `api_secret_key`.
3. Attacker replays this exact request to the app's webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header value with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the shared secret (`lib/shopify_api/webhooks/request.rb:35-43`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. The registered handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-200`), even though the body content came from the attacker's own shop — demonstrating the broken binding between the "authenticated" shop and the shop the handler is told to act on.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
