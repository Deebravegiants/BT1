Based on my review of the webhook processing code, I found a valid analog to the reported bug class (identity binding broken across a check).

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity using only the raw request body against the HMAC signature, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken directly from unauthenticated HTTP headers when dispatching to the host application's handler. This breaks the identity binding: `hmac-verified(body) != hmac-verified(shop)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, and then immediately forwards the *header-derived* `shop` (along with `topic`, `webhook_id`, `api_version`) to the app's registered handler as trusted metadata: [3](#0-2) 

Because the HMAC only proves "this body was signed using the app's `api_secret_key`" — it says nothing about which shop the body belongs to — any request with a body/HMAC pair that legitimately validates (for example, a genuine webhook payload previously delivered for the attacker's own installed shop) can have its `x-shopify-shop-domain` header swapped for an arbitrary other tenant's domain while still passing `Utils::HmacValidator.validate`, since the validator never inspects headers: [4](#0-3) 

This is the same class of bug as the reported Solidity issue: a privileged operation (`GaugeUpgradeable.setDistribution`) is gated on an identity check (`gaugeOwner()`) that is disconnected from the entity actually being mutated (`_gauge`), so the check passes for the wrong target. Here, the "signature is valid" check is disconnected from the "shop" identity that the signed payload is attributed to — the equality that should hold, `hmac_signed_shop == asserted_shop`, is never enforced because `shop` is not part of the signable string.

### Impact Explanation
Any host application that uses `data.shop` from `WebhookMetadata` to key its per-tenant lookups (session retrieval, data association, background job dispatch — exactly the documented usage pattern in `docs/usage/webhooks.md`) can be tricked into processing an attacker-controlled payload under a victim tenant's identity, i.e., cross-tenant data injection/confusion. This matches the "cross-tenant access" high/critical impact category, since the gem's own webhook-processing API is what host apps are told to trust for shop attribution.

### Likelihood Explanation
The attacker needs a valid (body, HMAC) pair. If the attacker controls their own shop installation of the app (a common SaaS multi-tenant scenario), they can receive their own legitimate webhook, capture the body and its valid HMAC, and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header pointing to a different tenant. No secret material is required beyond receiving one's own genuine webhook once. This is a realistic, unprivileged-attacker path through the gem's documented API surface.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the HMAC-verified payload rather than trusting the header value independently — e.g., require the host application to cross-check `data.shop` against the shop domain associated with the webhook subscription/session before acting, or extend `to_signable_string`/validation to incorporate the header-derived identity fields so a mismatch is rejected at the library layer. At minimum, document prominently that `data.shop` is not covered by the HMAC and must not be trusted as an authenticated tenant identifier by itself.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a legitimate webhook (e.g., `orders/create`), which Shopify signs with the app's shared `api_secret_key` over the raw body only.
2. Attacker captures the raw body and the valid `X-Shopify-Hmac-Sha256` header from this legitimate delivery.
3. Attacker replays the same body + HMAC to the app's webhook endpoint, but swaps `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `@raw_body` against the HMAC (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-22`).
5. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` = `"victim-shop.myshopify.com"` (attacker-controlled header) and dispatches it to the host app's handler as if it were an authentic event for the victim shop (`lib/shopify_api/webhooks/registry.rb:188-200`).

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
