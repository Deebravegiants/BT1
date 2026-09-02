### Title
Cross-tenant webhook spoofing via unauthenticated `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook only by validating the HMAC over the raw request body, but the `shop` (tenant identifier) that is handed to the app's handler is read from an HTTP header that is entirely excluded from that signature. This breaks the intended binding `hmac_verified(body) == authenticated(shop)`: the HMAC only proves *"this body was produced with the app's shared `client_secret`"*, it proves nothing about *which shop* the body belongs to.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body — the `shop` value is not part of the signed material: [2](#0-1) 

`shop` is instead read directly from an untrusted HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`), with no cryptographic tie to the signed body: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards the unauthenticated `request.shop` value straight to the app's webhook handler as the tenant identifier, alongside the (validated) body: [4](#0-3) 

Because a single app has one shared `client_secret` (`api_secret_key`) used to sign webhooks for *every* shop that installs it, any unprivileged internet user can install the target app on their own free/dev Shopify store, trigger a webhook, and receive a genuinely-HMAC-signed request (valid signature, attacker-controlled body content, attacker's real shop domain in the header). The attacker can then replay that exact HTTP request to the app's webhook endpoint while rewriting only the `shop-domain` header to a victim shop. `HmacValidator.validate` will still pass (the body/HMAC pair is untouched), so `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`. Any app logic that uses `shop` to key session lookup, tenant-scoped writes, or authorization decisions is fed a tenant identity that was never authenticated — the binding "shop that produced the signed bytes" == "shop passed to the handler" is false.

This is the same class of bug as the referenced report: `_notifyReward`/`vestTokens` mutates state (`lastUpdateTime`) without going through the binding step (`_updateReward`) that every other caller relies on, silently decoupling two values that must stay in sync. Here, `Registry.process` trusts `request.shop` as if it were bound to the verified HMAC, when in fact the signature computation (`to_signable_string`) never included it.

### Impact Explanation
This enables cross-tenant access: an attacker with no privileged credentials (no `api_secret_key`, no access token) can cause the host application to execute webhook-handler logic under an arbitrary victim shop identity, using a validly-signed-but-replayed body. Depending on how the host app's registered `WebhookHandler` uses `shop` (e.g., to look up/update the victim's stored session, toggle victim-tenant settings, or write attacker-controlled data into a victim-keyed record), this can result in cross-tenant data corruption or state manipulation — matching the "cross-tenant access" High/Critical impact category.

### Likelihood Explanation
Likelihood is high for any app built on this gem that does not itself add out-of-band binding between HMAC and shop (which the gem does not require or document as necessary). Obtaining a validly-signed body requires only installing the app on an attacker-owned store — a normal, unprivileged action — and capturing one webhook delivery. Replaying with a modified header is trivial with any HTTP client since headers are not covered by the signature or transport-level pinning enforced by this gem.

### Recommendation
Include the `shop-domain` value in the signable material used for webhook HMAC verification (mirroring how `AuthQuery#to_signable_string` binds `shop`, `host`, `code`, `state`, `timestamp` together). At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop domain (and other headers) into the value verified against the HMAC, or `Registry.process` should independently verify that the `shop` header matches an expected/registered shop before dispatching, rather than trusting it merely because the body's HMAC checked out.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (no special privilege needed — any Shopify Partner/dev store works).
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the raw HTTP request the app receives, including:
   - `x-shopify-hmac-sha256: <valid signature over raw body, computed with app's client_secret>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   - body: attacker-controlled JSON payload (order data can be crafted, e.g., custom line items, note attributes, ids).
3. Attacker replays the exact same request to the app's webhook endpoint but changes only the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` returns only `@raw_body` (unchanged from the original valid request):
```ruby
Utils::HmacValidator.validate(request) # => true, even though shop header was tampered with
```
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)`, causing the app to process attacker-controlled data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
