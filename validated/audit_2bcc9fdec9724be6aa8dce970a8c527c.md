Confirmed: the `to_signable_string` used for HMAC verification is only `@raw_body` [1](#0-0) , while the `shop` field consumed by the handler comes straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) . `Registry.process` only checks the HMAC and then forwards `request.shop` verbatim into `WebhookMetadata` for the app's handler [3](#0-2) [4](#0-3) . The HMAC is computed with `HmacValidator.validate_signature` over `verifiable_query.to_signable_string` (body only) and the single app-wide `Context.api_secret_key` [5](#0-4) , so the `shop` header is never part of the signed material.

### Title
Webhook `shop` identity is not covered by the HMAC, allowing cross-tenant impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::HmacValidator` authenticates only the raw request body against the app's shared `client_secret`; the `shop` (tenant) identity delivered to the app's webhook handler is read from an HTTP header that is completely outside the HMAC's coverage.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` [6](#0-5) , and for a webhook `Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor, however, is derived purely from the `shop-domain` header, which is never mixed into the HMAC input [2](#0-1) . `Registry.process` validates only the HMAC and then trusts `request.shop` as the tenant identity passed into the handler [3](#0-2) .

Because the app's `client_secret` (and thus the HMAC key) is identical for every shop that has the app installed, any shop that has installed the app can capture a legitimately-signed `(body, hmac)` pair from a webhook Shopify sends for its own store, and replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different value in the `shop-domain` (or `x-shopify-shop-domain`) header. `Utils::HmacValidator.validate` will still succeed, because it never inspects the header, and `Registry.process` will hand the forged `shop` value straight to the app's `WebhookHandler#handle` as trusted tenant identity [7](#0-6) .

This breaks the intended identity binding: `HMAC-verified(body) == shop-scoped action`. In reality the equality holds only for `HMAC-verified(body)`, while `shop` is attacker-controlled and unauthenticated.

### Impact Explanation
Any application built on this gem that keys authorization, data writes, or lookups off `WebhookMetadata#shop` is exposed to cross-tenant data corruption or disclosure: an attacker who controls one shop (a normal, unprivileged merchant) can trigger handler logic that operates as if the event originated from an arbitrary other shop the attacker does not control, without needing that other shop's access token or `client_secret`. This matches the "cross-tenant access" Critical impact category, since no privileged credentials for the victim shop are required — only a webhook naturally delivered to the attacker's own store.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop (a normal onboarding flow available to anyone), (2) capturing one legitimate webhook `(body, hmac)` pair sent to that shop, and (3) POSTing it to the app's public webhook endpoint with a modified `shop-domain` header. No secrets, tokens, or elevated privileges are needed, making this practically reachable by any unprivileged internet user who can install the app.

### Recommendation
Bind the `shop` value into the authenticated material, e.g., include the `x-shopify-shop-domain` header (and/or `topic`, `webhook-id`) as part of the HMAC-signed string in `to_signable_string`, or otherwise cross-check the header-provided shop against an independently verified source (such as a per-shop record keyed by an authenticated identifier) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any subscribed event (e.g., `orders/create`) on their own shop, capturing Shopify's POST: body `B`, and header `x-shopify-hmac-sha256` = `H` (valid because it's signed with the app's real `client_secret`), along with `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H`, so `Registry.process` proceeds and calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to act as though the (attacker-controlled) payload originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L14-24)
```ruby
    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
