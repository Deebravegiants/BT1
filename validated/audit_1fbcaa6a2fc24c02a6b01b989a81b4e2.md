### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once the HMAC check passes, then trusts the `shop-domain` (and `topic`) HTTP headers taken directly from the request to build the `WebhookMetadata` handed to the app's handler. The HMAC, however, only signs the raw request body — not the `shop-domain` header — so the "verified" identity (HMAC over body) and the "acted-upon" identity (shop attribution taken from an unauthenticated header) are different bindings. Anyone who can obtain one legitimate `(raw_body, hmac)` pair (e.g., by installing the app on their own free/dev store and receiving a real webhook) can resend that exact body+HMAC pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain, causing the app to process attacker-controlled webhook data attributed to a different, unrelated tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only computes the HMAC over `to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` uses this body-only check as the sole authentication gate, then immediately forwards the unauthenticated `request.shop` header value to the app's handler as the trusted tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`HMAC-verified bytes == bytes the handler acts on for tenant attribution`

In reality:
`HMAC-verified bytes == raw_body only`, while
`bytes the handler acts on for tenant attribution == shop-domain header (unsigned)`

Because the two are not the same, a valid HMAC over *some* body says nothing about which shop that body belongs to. The gem's own documentation reinforces the false assumption that `process` fully authenticates the request: "This will verify the request did indeed come from Shopify" (docs/usage/webhooks.md), which is not true for the `shop` attribution — only the body is verified as being signed with the app's shared secret.

Note that the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that has installed the app — it is not shop-specific. So any attacker who installs the app on their own store (an ordinary, unprivileged action available to any internet user) will receive real, validly-signed webhooks for their own store, and can replay the identical `(raw_body, hmac)` pair against the app's webhook endpoint with the `shop-domain` header changed to a victim's `*.myshopify.com` domain (public/guessable information).

### Impact Explanation
This breaks a tenant boundary: an unprivileged app-installer (attacker on their own store) can inject webhook events into the host application that are attributed to a different merchant's shop. Depending on how the host app uses `WebhookMetadata#shop` (commonly used as a lookup key to load the target shop's session/data before acting on the payload), this can produce cross-tenant data corruption or trigger shop-scoped side effects (e.g., forged `app/uninstalled`, `shop/redact`, `customers/data_request`, or resource-mutation events) for a shop the attacker does not control. This matches the "Critical — cross-tenant access" impact category, since the gem's `process` API is the exact trust boundary a host app relies on and it fails to bind the authenticated payload to the shop it reports.

### Likelihood Explanation
No privileged credentials, tokens, or social engineering are required. Any internet user can install the target app on a store they control (many apps offer free installs/dev stores) to legitimately harvest a `(raw_body, hmac)` pair, then replay it against the same app's public webhook endpoint with a forged `shop-domain` header. The attack requires no cryptographic secret and no interaction with the victim.

### Recommendation
- Bind `shop`, `topic`, and other Shopify-supplied metadata into the value that is HMAC-verified, or independently re-derive/validate the reported shop (e.g., cross-check `request.shop` against a shop that the app has an active, previously-established session/installation record for) before invoking the handler.
- Update `ShopifyAPI::Webhooks::Request#to_signable_string` or `Registry.process` to make clear that only body integrity is verified, and document that host applications MUST additionally verify that the reported shop is a known, currently-installed tenant before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., updates a product to fire `products/update`).
2. Attacker captures the legitimate request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `HMAC-SHA256(api_secret_key, B) == H`), along with `X-Shopify-Topic: products/update`.
3. Attacker resends the exact same `B` and `H` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) succeeds because it only checks `B` against `H`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata.new(topic: "products/update", shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` and invokes the app's handler as if `victim-shop` sent this update — despite the payload actually originating from the attacker's own store.

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
