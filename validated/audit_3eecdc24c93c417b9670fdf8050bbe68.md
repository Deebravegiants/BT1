### Title
Webhook shop-domain identity not covered by HMAC signature allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) for a webhook from an unauthenticated HTTP header, while the HMAC signature that this gem verifies covers only the raw request body. This breaks the identity binding `signed_bytes == shop_attributed_to_data`, letting an attacker who can obtain one validly-signed webhook body (e.g. from their own store, since the app's `client_secret`/HMAC key is shared across every shop that installs the app) replay that body against the app's webhook endpoint while substituting an arbitrary `shop-domain`/`shop-domain` header value, causing the app to process/attribute attacker-chosen webhook data to a different (victim) tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the material that is actually signed: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`; `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers and are never part of the signed payload: [3](#0-2) 

`Utils::HmacValidator.validate` verifies the HMAC purely against `to_signable_string` (i.e., the raw body) using `Context.api_secret_key`: [4](#0-3) 

`Registry.process` checks this HMAC, then forwards the **unverified** `request.shop` header straight to the app's webhook handler as the tenant identifier, with no further cross-check against the signed content or the topic's registered shop: [5](#0-4) 

The `client_secret` (`Context.api_secret_key`) used to compute this HMAC is a single per-app secret shared by Shopify across every merchant store that installs the app — it is not shop-specific. Consequently, any internet user who can install the app on their own store (a normal, unprivileged action) can:
1. Trigger a webhook topic on their own store to obtain a `(raw_body, valid_hmac)` pair signed with the app's shared secret.
2. Replay that exact body and HMAC to the app's public webhook endpoint, but with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header changed to a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it only checks the body bytes against the same shared secret), and `Registry.process` dispatches `WebhookMetadata.new(shop: <victim-shop>, ...)` to the handler, exactly as if the victim shop had generated that event.

This is the same bug class as the reference finding: a piece of application data that downstream logic keys off of (`depositCalldata` → routing bytes decoded into public keys; here, `shop` → tenant the webhook data gets attributed/persisted to) is not included in the cryptographic binding (guardian signature / HMAC) that is meant to authenticate the whole request.

### Impact Explanation
Any host application that uses `data.shop` from `WebhookMetadata` to decide which tenant's records to update, upsert, or delete (the documented and expected usage pattern shown in `docs/usage/webhooks.md`) is exposed to cross-tenant data confusion/corruption: an attacker-controlled shop can inject webhook events that get attributed to and processed against a different merchant's data, without needing that merchant's access token or any other merchant-specific secret. This matches the "cross-tenant access" criterion for a Critical-impact finding.

### Likelihood Explanation
Exploitation only requires the attacker to be an app-installing merchant (an unprivileged internet user relative to other tenants) and to control the webhook endpoint's reachable topic/body content on their own store — both are ordinary, unauthenticated-relative-to-victim actions. No access token, refresh token, or leaked credential of the victim is required; only the app's already-shared HMAC secret behavior is (mis)used as designed.

### Recommendation
Bind the tenant identity into the verified signature material, or verify it out-of-band against server-side state:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in `to_signable_string`/the HMAC computation, mirroring the deposit-calldata fix recommendation (hash the additional fields into the signed message), or
- Cross-check `request.shop` against the shop that the app's own persisted webhook subscription/session store expects for that `webhook_id`/topic before dispatching to the handler, rejecting mismatches.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on `victim-shop.myshopify.com`, both under the same Partner app / `client_secret`.
2. Attacker triggers a normal webhook (e.g. `orders/create`) on their own shop, capturing the raw body `B` and the resulting header `X-Shopify-Hmac-SHA256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker POSTs to the victim app's webhook endpoint with body `B`, header `X-Shopify-Hmac-SHA256: H` (unchanged, still valid), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` → `Utils::HmacValidator.validate` passes (per `lib/shopify_api/utils/hmac_validator.rb:12-31`, only `B` and `H` are checked), and the handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` per `lib/shopify_api/webhooks/registry.rb:198-199`, causing the app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
