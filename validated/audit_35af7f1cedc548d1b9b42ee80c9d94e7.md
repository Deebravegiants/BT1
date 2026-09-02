### Title
Webhook `shop-domain` header is trusted as the tenant identity but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature from the raw body only, while the `shop` (and `topic`) values come from separate, unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that HMAC and then hands the header-derived `shop` straight to the app's handler as the authenticated tenant identifier, even though the documentation promises this call "will verify the request did indeed come from Shopify."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `api_version`, and `webhook_id` are all read from separate HTTP headers that are never fed into the signable string: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate` / `#validate_signature` — only checks `verifiable_query.to_signable_string` (i.e. the raw body) against the received HMAC: [3](#0-2) 

After that check passes, `process` immediately builds `WebhookMetadata` from `request.shop` — the unauthenticated header value — and dispatches it to the app's handler as the tenant identity: [4](#0-3) 

The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request (including the shop attribution) is authenticated: [5](#0-4) 

This is the exact identity-binding break called out in the rules: a field acted on (`shop`, used as the tenant/session key passed to the handler) is not covered by the HMAC that is verified (only the raw body is). Since the same `api_secret_key` HMAC secret is shared across every shop that installs the app, any shop that has installed the app can legitimately receive a validly-HMAC'd webhook body for its own store, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `shopify-shop-domain`) header for a victim shop. Because the header is outside the signed content, `HmacValidator.validate` still returns `true`, and the forged `shop` value flows unauthenticated into `WebhookMetadata#shop` and thus into the host application's tenant-scoped business logic (e.g., "look up victim shop's session/store and act on `body`").

### Impact Explanation
This crosses a tenant boundary: an unprivileged holder of a legitimate app installation (their own shop) can make the app process/attribute arbitrary webhook data under a different shop's identity, because the binding `authenticated-bytes == acted-upon shop` does not hold — the gem verifies bytes of the body but parses/acts on a different, unverified field (the shop domain) for tenant attribution. Any app that uses `data.shop` from the handler to select which merchant's session/data-store to write to (the documented, expected usage pattern) is exposed to cross-tenant data injection/corruption using only a legitimate app install of the attacker's own store — no `api_secret_key`, access token, or privileged access required.

### Likelihood Explanation
Requires only that the attacker's own shop have the app installed and be able to receive/relay at least one webhook (baseline capability of any merchant that installs the app) and replay it with a modified header to the app's public webhook endpoint. No secrets, tokens, or additional access are required, and the surface (webhook headers vs. HMAC-covered body) is exactly as designed/documented in this gem — the gem does not bind `shop` into the signature nor warn callers that `data.shop` is unauthenticated despite `process` being advertised as full verification.

### Recommendation
Include `shop` (and ideally `topic`/`webhook-id`) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived shop to the verified body (e.g., require callers to cross-check `data.shop` against a known/authenticated session store before using it), and update the documentation to make clear that `Registry.process` only authenticates the raw body, not the shop-domain header.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal merchant onboarding).
2. Shopify sends a legitimate webhook to the attacker for a topic they control, e.g. `{"id":1}` with headers `x-shopify-hmac-sha256: <valid HMAC of body with app secret>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical raw body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Webhooks::Request#hmac`/`#to_signable_string` only look at the raw body, so `HmacValidator.validate` returns `true` — [6](#0-5)  and [7](#0-6) .
5. `Registry.process` calls the app handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id":1}, ...)` — [8](#0-7)  — causing the host app to act on attacker-supplied data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
