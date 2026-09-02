### Title
Webhook `shop` identity is trusted from an unauthenticated header while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by checking that `X-Shopify-Hmac-Sha256` matches an HMAC of the **raw body only**. The `shop` identity that is forwarded to the app's handler (and typically used to load the tenant's session/store data) is read straight from the `X-Shopify-Shop-Domain` header, which is **not part of the signed content**. The binding the gem should guarantee is `hmac == HMAC(secret, raw_body ‖ shop)`; what it actually guarantees is `hmac == HMAC(secret, raw_body)`, i.e. the body's authenticity says nothing about which shop it is attributed to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is parsed from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never fed into `to_signable_string` and therefore never covered by the HMAC: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the raw body) and compares it to the caller-supplied `hmac`: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then immediately trusts `request.shop` (the unauthenticated header) to build the `WebhookMetadata` that is handed to the app's handler for tenant attribution: [4](#0-3) 

Because the header is outside the signed material, any HTTP client that possesses one previously-valid `(raw_body, hmac)` pair (e.g., an attacker who installed the app on their own shop and received a legitimate webhook for it) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. `Utils::HmacValidator.validate` still returns `true` because the body was not altered, but `Registry.process` now calls the handler with a `shop` value chosen entirely by the attacker instead of the shop that actually produced the payload — the classic "field acted on but not covered by the HMAC" pattern from the report, mapped onto the `shop == shop-that-authorized-the-body` binding.

### Impact Explanation
This breaks the tenant boundary that host applications rely on this gem to enforce: `WebhookMetadata#shop` is the value most Shopify apps use to look up or attribute session/store data for the webhook. An attacker-controlled `shop` value delivered through a channel presented as "validated" (because `Utils::HmacValidator.validate(request)` passed) can cause the app to process/store attacker data under a victim shop's identity — cross-tenant access/confusion, without needing the app's `api_secret_key`, an access token, or any privileged account. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The only prerequisite is the ability to trigger one genuine webhook delivery for a shop the attacker controls (installing the app on their own store, or on a free/dev store, is an unprivileged action) and the ability to POST directly to the app's public webhook endpoint with custom headers — both squarely within an unprivileged internet user's capability. No secret material or victim credentials are required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically tie the header values to the verified body, e.g., by including the shop domain in `to_signable_string`, or by deriving the shop from Shopify's per-shop HMAC secret if using shop-specific secrets, so `Utils::HmacValidator.validate` proves both the payload and its claimed origin.

### Proof of Concept
1. Attacker installs the target app on their own Shopify dev/free store (`attacker-shop.myshopify.com`) and triggers a webhook (e.g., `orders/create`).
2. Attacker's endpoint (or intercepted traffic) captures the exact raw request body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(secret, B)`.
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC_SHA256(secret, B)`, which still equals `H`, so validation passes (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the app's handler with the victim's shop identity attached to attacker-supplied data.

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
