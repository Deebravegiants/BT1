### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` verify the HMAC over the webhook **body only**, while the `shop`, `topic`, `webhook_id`, and `api_version` values that identify *which tenant* the payload belongs to are read directly from unauthenticated HTTP headers and are never included in the signed content. This breaks the binding `shop-that-signed-the-body == shop-attributed-to-the-handler`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

But `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled straight from caller-supplied headers with no cryptographic binding to the body or its HMAC: [2](#0-1) 

`Registry.process` validates only the body-derived HMAC, then forwards the unvalidated `request.shop`, `request.topic`, and `request.webhook_id` straight into the handler metadata: [3](#0-2) 

`HmacValidator.validate` confirms only that the body bytes match a HMAC computed with the app secret — it has no knowledge of, and does not cover, the `shop-domain`, `topic`, or `webhook-id` headers: [4](#0-3) 

Because any two of `{body, hmac}` pairs are transferable as long as they are self-consistent, and the `shop-domain` header used for tenant attribution is entirely outside that HMAC, an attacker who can obtain **any one legitimately signed webhook delivery** (e.g., by installing the app on their own store, which is an unprivileged, self-service action any internet user can take) can replay that exact `body` + `hmac-sha256` pair to the app's public webhook endpoint while substituting an arbitrary victim's `x-shopify-shop-domain` header. `Utils::HmacValidator.validate` will still return `true` because it only re-hashes the (unchanged) body, and `Registry.process` will hand the handler a `WebhookMetadata` object claiming the body belongs to the attacker-chosen victim shop.

This is the same bug class as the report's core issue — an unprivileged actor exploiting a mismatch between "what was cryptographically verified" (bytes verified) and "what the caller uses for tenant/entity attribution" (bytes acted upon) — applied here to the shop-identity binding instead of the withdrawal-proof binding.

### Impact Explanation
Any host application that follows this gem's documented webhook contract (using `WebhookMetadata#shop` — the value produced by this vulnerable code — to key persistence, authorization, or side effects per merchant) can be made to attribute attacker-controlled payload content to an arbitrary victim shop. This is a cross-tenant access primitive: data or actions intended for tenant B can be triggered/attributed using a payload that was only ever legitimately signed for tenant A (the attacker's own shop). Given the gem's own API surface offers no way for the host app to independently verify shop identity beyond `HmacValidator.validate` + `request.shop`, this crosses into the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The attacker only needs to install the app for free/at low cost on a shop they control (an ordinary, unprivileged flow) to obtain one valid `(body, hmac)` pair, then replay it against the same public webhook URL with a forged `x-shopify-shop-domain` header. No credentials, tokens, or `api_secret_key` access are required — only the ability to send an HTTP POST with attacker-chosen headers, which is inherent to any public webhook endpoint.

### Recommendation
- Include `shop`, `topic`, and `webhook_id` (or minimally `shop`) in the value that is HMAC-verified, or independently cross-check `request.shop` against a value bound to the delivery (e.g., validate that the shop domain matches an active, previously-established session/installation record) before dispatching to the handler.
- At minimum, document/enforce in `Registry.process` that `request.shop` must not be trusted as an identity boundary unless the host app independently authenticates it, since the current HMAC check gives false confidence that the whole `Request` object (including `shop`) was verified.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery for topic `customers/data_request` with body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S`).
2. Attacker replays an HTTP POST to the app's public webhook endpoint with:
   - `x-shopify-hmac-sha256: H` (unchanged)
   - Body: `B` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic: customers/data_request` (unchanged or forged, also uncovered by HMAC)
3. `ShopifyAPI::Webhooks::Request.new` parses these headers.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` (`B`) only, matching `H` — validation succeeds. [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: B, ...)`, attributing attacker-controlled data `B` to the victim shop.

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
