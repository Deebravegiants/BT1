This confirms the gem's own documentation explicitly claims `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" as a whole — and that `data.shop` is documented as a trusted output field of that verification (`docs/usage/webhooks.md:125`, `docs/usage/webhooks.md:14`). That's sufficient to finalize the analog.

### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted without HMAC binding, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking `Utils::HmacValidator.validate(request)`, which validates the HMAC over the raw body only. The `shop`, `topic`, `webhook_id`, and `api_version` values that the registry hands to the app's handler are read directly from HTTP headers and are never covered by that HMAC, so they carry no cryptographic binding to the verified payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

All other identity fields are pulled straight from attacker-suppliable headers with no signature coverage: [2](#0-1) 

`Registry.process` treats a passing `HmacValidator.validate` call as proof the whole request "did indeed come from Shopify" (per the gem's own docs) and then forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` to the developer's handler: [3](#0-2) 

`HmacValidator.validate` computes the digest over `verifiable_query.to_signable_string` (i.e., body bytes only) and secure-compares it to the `hmac` header: [4](#0-3) 

The identity binding that should hold is: `bytes verified by HMAC == bytes the handler acts on`. Here it breaks down to `bytes verified by HMAC (raw_body) != identity fields acted on (shop-domain, topic, webhook-id headers)`. The webhook signing key (`Context.api_secret_key`) is shared across every merchant that has installed the app — it is not shop-specific. This means any unprivileged user who installs the app on their own (attacker-controlled) store legitimately receives, from Shopify, one or more valid `(raw_body, hmac)` pairs signed with the app's real secret. Because the `shop-domain` header carries no signature coverage, the attacker can replay that exact `(raw_body, hmac)` pair directly against the app's public webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body/hmac pair is genuinely valid), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain and `body` set to attacker-controlled content, all despite that payload never having been signed for that shop.

This is a direct analog of the reported bug class: a field (`shop`, here playing the role of the path/identity value) is acted upon by the trusted post-verification code path, but that field is not covered by the same integrity check (HMAC) that gates the "verified" branch — mirroring how `cache_path`/`cache_file` in the original report acted on `path` data that was never subjected to the traversal check that gated the "safe" branch.

### Impact Explanation
This breaks the tenant-isolation guarantee applications rely on. Any code that uses `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) to key persistence, deduplication, or state changes (exactly the pattern the gem's own docs recommend at `docs/usage/webhooks.md:26`, `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to attribute attacker-supplied webhook bodies to a shop the attacker does not control. This is a cross-tenant data-integrity/confusion vector reachable by any user who can install the target app on a store they control — no `api_secret_key`, access token, or privileged account is required.

### Likelihood Explanation
Any developer or free-plan merchant can install a public Shopify app, trigger an event that fires a subscribed webhook topic for their own store, and capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair from the wire. The app's webhook endpoint is a public, unauthenticated HTTP route by design (per `docs/usage/webhooks.md:125`), so replaying that pair with a modified `shop-domain` header requires nothing beyond basic HTTP tooling.

### Recommendation
Bind the identity headers into the HMAC-verified surface, e.g., include `shop-domain`, `topic`, and `webhook-id` in `to_signable_string` (or otherwise cryptographically bind them, since Shopify signs the body only), or — at minimum — require callers to separately corroborate `request.shop` against an expected/known session shop before acting on webhook data, and document this gap prominently so host apps cannot mistake `HmacValidator.validate` for full request authentication.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and subscribes to a topic (e.g. `orders/create`) via `ShopifyAPI::Webhooks::Registry.register`.
2. Attacker triggers the event on their own store; Shopify legitimately POSTs to the app's webhook endpoint with a genuine body `B` and a valid `x-shopify-hmac-sha256` header `H` (computed by Shopify using the app's real `api_secret_key`), along with `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` and re-sends an HTTP POST directly to the app's public webhook route with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` and matches `H` — validation passes.
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data attributed to `victim-shop.myshopify.com`.

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
