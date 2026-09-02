This confirms the analog: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` and never includes `shop`, `topic`, or `webhook_id`, so the HMAC in `Registry.process` verifies body integrity only — the `shop-domain` header used to identify the tenant is not bound by the signature.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` accepts a webhook as authentic once `Utils::HmacValidator.validate(request)` passes. That validation only proves that the *body bytes* were signed by the app's `client_secret`; the `shop` (from the `x-shopify-shop-domain` / `shopify-shop-domain` header) that identifies which merchant/tenant the webhook belongs to is never part of the signed material, so it can be freely substituted by anyone who can produce a validly-signed body.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e. the raw body only) before dispatching to the handler with the unauthenticated `request.shop` value: [3](#0-2) 

`HmacValidator.validate` simply recomputes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the supplied `hmac`: [4](#0-3) 

This exactly matches the report's bug class: a field that is *acted on* (here, the `shop` used to route/attribute the webhook to a tenant) is *not covered* by the cryptographic commitment (here, the HMAC), even though a downstream verification step (`decreasePendingDepositBalance`-equivalent tenant check) is assumed to have validated it. Since all shops that install the same app share the single `client_secret` used to sign every webhook, any shop owner who has installed the app can capture a legitimately-signed webhook body delivered to their own shop, then resubmit it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a *different* victim shop. The HMAC still validates (it only covers the body), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: <victim shop>, body: <attacker's own body>, ...)`.

### Impact Explanation
If the host application trusts `WebhookMetadata#shop` (as intended and documented) to determine which merchant's session/data record the webhook body applies to, an attacker can inject webhook data attributed to an arbitrary other tenant's shop domain, achieving cross-tenant data confusion/access without ever needing that tenant's credentials — matching the "Critical: cross-tenant access" impact class. The equality being broken is: `authenticated(shop signing this webhook) == shop label acted upon`; the gem enforces `authenticated(body) == received(body)` but never binds `shop` into that check.

### Likelihood Explanation
Requires only that the attacker run their own instance of the app (i.e., install it on a shop they control, or capture any webhook payload for a topic they can trigger) — no special privilege, employee access, or leaked secret is needed. This is fully reachable by any unprivileged internet user who can install a public/dev app or observe webhook traffic to their own shop.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signable material verified against the HMAC, or independently authenticate the `shop` header against a known, previously-established relationship (e.g., verify it against the session/token associated with the webhook subscription) before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify delivers a request with a valid `x-shopify-hmac-sha256` signed with the app's `client_secret` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture the raw body and HMAC header value.
3. Replay the identical raw body and HMAC to the app's webhook endpoint, but rewrite `x-shopify-shop-domain` (or `shopify-shop-domain`) to `victim.myshopify.com`.
4. `Webhooks::Request.new` accepts the forged headers, `Utils::HmacValidator.validate` succeeds (it only hashes `@raw_body`), and `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: attacker-controlled JSON)` — the handler cannot distinguish this from a genuine webhook for `victim.myshopify.com`.

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
