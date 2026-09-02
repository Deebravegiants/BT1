## Analysis

The relevant vulnerability class here is a field that is acted upon by the application but not covered by the HMAC signature — specifically in the webhook verification path.

Look at [1](#0-0) : `ShopifyAPI::Webhooks::Request` exposes `shop` by reading the `x-shopify-shop-domain` header directly, while `to_signable_string` (the data that is actually HMAC-verified) returns only `@raw_body`. The `shop` value is never mixed into the signed material.

`ShopifyAPI::Webhooks::Registry.process` then trusts this unverified header value and forwards it straight into the handler: [2](#0-1) . `Utils::HmacValidator.validate` only proves that `raw_body` was signed with the app's shared secret [3](#0-2) ; it says nothing about which shop that body belongs to.

### Title
Webhook shop-domain is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop` is read straight from the (unauthenticated) `X-Shopify-Shop-Domain` header. `Registry.process` validates the HMAC against the body only, then passes the header-derived `shop` value to the app's webhook handler as if it were verified.

### Finding Description
The identity binding that should hold is:
`HMAC_verified(raw_body) == shop_attributed_to(raw_body)`

But in this gem that equality is broken: `HmacValidator.validate` proves only that `raw_body` was signed with `Context.api_secret_key` (or `old_api_secret_key`) [4](#0-3) . The `shop` attribute used by `Registry.process` to build `WebhookMetadata` comes from a header that is completely outside the signed payload [5](#0-4) [6](#0-5) .

Because the app's `api_secret_key` (client secret) is shared across every shop that installs the app, any unprivileged merchant who has legitimately installed the app on their own store can trigger Shopify to deliver a legitimate, correctly-signed webhook for their own shop with attacker-chosen body content (e.g., an order note, product title, or metafield value). That request/HMAC pair is valid for *that specific body*, regardless of which shop domain header accompanies it. The merchant can then replay the identical `raw_body` + HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (or `Shopify-Shop-Domain`) with a victim shop's domain. `HmacValidator.validate` will still return `true` (since the signature only covers `raw_body`), and `Registry.process` will call the handler with `WebhookMetadata.shop` set to the victim's domain [7](#0-6) .

### Impact Explanation
This allows cross-tenant data injection: an attacker-controlled webhook body can be attributed to any other merchant's shop domain that the app hosts. Any host application that keys per-shop state, records, or side effects off `WebhookMetadata#shop` (which is the gem's documented contract, see `docs/usage/webhooks.md`) will process attacker-supplied data under a victim tenant's identity — a cross-tenant access/data-integrity break, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker (1) installs the target app on their own store (an unprivileged, ordinary onboarding action) and (2) knows or guesses a victim shop's `.myshopify.com` domain (often discoverable/public). No access to `api_secret_key`, access tokens, or the app's infrastructure is required — only the ability to trigger a webhook for their own store and replay the resulting HTTP request with a modified header, which is squarely within an "unprivileged internet user" threat model.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise cryptographically tie `shop` to the signed body — e.g., include the `shop-domain` header (and ideally `webhook-id`/`topic`) in `to_signable_string`, or require host applications to independently corroborate the shop with a value obtained from a trusted source (such as a previously stored, verified session) rather than trusting the header outright.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers an event (e.g., updates an order note) causing Shopify to deliver a legitimately HMAC-signed webhook: body `B`, `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same body `B` and signature `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) and matches `H` — validation succeeds [8](#0-7) .
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [7](#0-6)  — attacker-controlled data is now processed under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
