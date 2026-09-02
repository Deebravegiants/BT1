## Title
Webhook Shop/Topic Identity Spoofing via HMAC Scope Gap - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, while the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) are read from HTTP headers that are never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` trusts these header-derived fields and hands them straight to the app's webhook handler once the body-only HMAC check passes, so the "which shop does this payload belong to" binding is never actually authenticated by the gem.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are pulled straight from attacker-visible/attacker-settable HTTP headers with no cryptographic binding to the body that was actually signed: [2](#0-1) 

`Utils::HmacValidator.validate` (invoked from `Registry.process`) only recomputes and compares the HMAC over `to_signable_string`, i.e. the body — it never verifies `shop`, `topic`, `webhook_id` or `api_version`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`/`request.topic`, which is delivered to the app-registered handler as the trusted tenant identity for that payload: [4](#0-3) 

Because the app's webhook secret (`api_secret_key`) is shared across every shop that installs the app (it is not per-shop), any user who legitimately installs the app on their own store can trigger a genuine webhook delivery and thereby obtain a valid `(raw_body, hmac)` pair signed with the app's single secret. Since the header fields are outside the signed scope, that same `(raw_body, hmac)` pair can be replayed to the app's public webhook endpoint with the `shop-domain` header rewritten to a different (victim) shop. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` will dispatch the payload to the handler labeled as coming from the victim shop.

The broken identity binding, stated as an equality that should hold but doesn't:
`shop the HMAC was computed for` (i.e., the shop whose Shopify-side webhook delivery produced this exact body+hmac) **≠** `shop passed to the handler as request.shop` (attacker-controlled header, unverified).

### Impact Explanation
This is a cross-tenant identity confusion: an app that uses the `shop` value from `WebhookMetadata` to key writes, decide which merchant record to update, or select which access token/session to act with, can be made to attribute one shop's webhook data (or a replayed/crafted body under the attacker's control) to a completely different, unrelated shop. Any app that stores webhook payload data keyed by `data.shop` (the officially documented and intended way to use this field — see `handler.handle(data: WebhookMetadata.new(...))`) inherits this cross-tenant write/read primitive purely because the gem does not bind `shop` to the HMAC signature it verifies.

### Likelihood Explanation
Any actor who can install the target app on any store (including a free/trial development store) can capture a legitimate `(body, hmac)` pair for a webhook topic of their choosing, since Shopify signs with the single app-wide `api_secret_key` rather than a per-shop secret. No possession of `api_secret_key`, access tokens, or other privileged material is required — only the ability to trigger one real webhook delivery to themselves and then replay it against the same public endpoint with a modified `shop-domain`/`topic` header.

### Recommendation
Bind the tenant/topic identity into the verified material instead of trusting bare headers after a body-only HMAC check:
- Include `shop`, `topic`, and `webhook_id` in the signable string used by `HmacValidator`, or
- Independently verify that `request.shop` corresponds to a shop with an active, stored session/installation before invoking the handler, and treat header-derived `shop`/`topic` as untrusted input until that check passes.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify delivers a request to the app's public webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed with the app's single `api_secret_key`).
2. Capture `B` and `H` (e.g., via a logging proxy under the attacker's control, since it is the attacker's own shop's traffic).
3. Replay the exact same request to the app's public webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`: [3](#0-2) 
5. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the app's handler, which now processes attacker-supplied data under the victim's shop identity: [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
