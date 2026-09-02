### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, and `webhook_id` values are read straight from HTTP headers with no cryptographic binding to that signature. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards the unverified `shop` header value directly to the application's webhook handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Request#shop`, `#topic`, and `#webhook_id` are parsed straight from headers with no signature coverage: [2](#0-1) 

`Registry.process` validates only this body-derived HMAC via `Utils::HmacValidator.validate(request)`, then passes `request.shop` unchanged into the `WebhookMetadata` handed to the application handler: [3](#0-2) 

`HmacValidator.validate_signature` computes the digest from `verifiable_query.to_signable_string` (the raw body) using the app-wide `Context.api_secret_key`/`old_api_secret_key`, which is the same secret for every shop that has the app installed — it is not shop-specific: [4](#0-3) 

Because the same `client_secret` verifies webhooks for *every* installed shop and the `shop-domain` header is excluded from the signed content, the equality the code implicitly relies on breaks down:
`shop_header_used_by_handler == shop_that_actually_produced_the_signed_body` is never checked; only `hmac(raw_body, api_secret_key)` is checked, independent of which shop it came from.

An attacker who has installed the app on their own (attacker-controlled) shop will legitimately receive webhook deliveries containing a valid `x-shopify-hmac-sha256` value computed with the shared `api_secret_key` over a body they can freely craft as much as Shopify's payload schema allows (e.g. for topics with attacker-influenced content, or simply replaying/relabeling a captured payload). The attacker can then resend that exact `(raw_body, hmac)` pair to the victim application's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header pointing at a different, victim shop. Because `to_signable_string` never includes the shop, the HMAC still validates, and `Registry.process` forwards the attacker-chosen shop value to the handler unaltered.

### Impact Explanation
This breaks the tenant identity binding a multi-tenant app relies on when dispatching webhook data by `WebhookMetadata#shop`: a handler that looks up or mutates per-shop state keyed by `data.shop` (e.g., session/token lookup, inventory sync, mandatory GDPR topics such as `shop/redact`) can be made to act on/for a shop the attacker does not control, using data whose authenticity was only proven for the attacker's own shop. This is a cross-tenant boundary violation reachable by any user who can install the app on a shop they control — no `api_secret_key`, access token, or privileged account is required from the attacker's side.

### Likelihood Explanation
Likely reachable in any deployment that (a) allows installation on attacker-controlled/free development shops and (b) has a webhook handler that branches or persists data based on `WebhookMetadata#shop` without independently re-validating the shop against session/token records. The gem's public API (`Registry.process`) gives no way for the host app to detect this, since it explicitly reports the request as HMAC-valid.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed/verifiable content, or independently cross-check `request.shop` against a shop known to be associated with the specific webhook subscription/session before dispatching to handlers. At minimum, document prominently that `shop-domain` is unauthenticated and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; Shopify sends a real webhook with header `x-shopify-shop-domain: attacker.myshopify.com`, body `B`, and `x-shopify-hmac-sha256: HMAC(B, client_secret)`.
2. Attacker replays the same `B` and HMAC value to the app's webhook endpoint, replacing the header with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(B, client_secret)`: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` and processes the attacker's body as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
