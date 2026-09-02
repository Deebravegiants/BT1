This confirms the vulnerability. The webhook `hmac-sha256` signature is computed only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` field consumed by the handler comes from the `x-shopify-shop-domain`/`shopify-shop-domain` header — a value that is never included in the HMAC signable string.### Title
Webhook `shop` field is not covered by the HMAC signature, allowing shop-domain spoofing across tenants - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating only the HMAC over the raw request body, but the `shop` attribute that is subsequently trusted and handed to the app's `WebhookHandler` is read from an HTTP header that is never part of the signed payload. This breaks the intended binding `HMAC-authenticated bytes == bytes the app attributes to a given shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is instead read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` signs/verifies only `verifiable_query.to_signable_string`, i.e., only the body — the `shop` header plays no role in the signature computation: [4](#0-3) 

Because Shopify computes the webhook HMAC as `HMAC-SHA256(client_secret, raw_body)` and the `client_secret` is per-app (shared across every shop that installs the app), the *same* signature is valid for the *same* body **regardless of which shop it originated from**. Any attacker who has legitimate access to a shop with the app installed (a merchant customer, or someone who can trigger a webhook with a predictable/empty/identical body such as `{}` payloads common to several topics) can capture a genuine `raw_body` + `hmac-sha256` pair from their own store, then replay that exact body and signature to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it never inspected the shop header, and `Registry.process` forwards `shop: request.shop` (the attacker-controlled value) straight to `handler.handle`, which per the documented contract is expected to look up shop-specific state/tenant using that field: [5](#0-4) 

The equality broken is: `shop authenticated by the HMAC (none)` vs `shop the handler acts on (attacker-supplied header)` — a textbook identity-binding gap fitting the rule's "a field acted on but not covered by the HMAC" category.

### Impact Explanation
This is a cross-tenant confusion vector: an application built on this gem's documented `WebhookHandler` API (per `docs/usage/webhooks.md`) that uses `data.shop` to select which tenant's records to update, delete, or reprocess (e.g., `customers/redact`, `shop/redact`, `orders/create`, `app/uninstalled`) can be tricked into applying an event meant for the attacker's shop to a different, victim shop, or vice versa — without needing the app's `client_secret`, an access token, or any privileged credential. This satisfies the High-impact bar ("scope or expiry check bypass"/tenant boundary confusion via a credential-adjacent identity check) since the trust boundary the gem is supposed to enforce (webhook signature authenticates *which shop* sent data) is not actually enforced.

### Likelihood Explanation
Exploitability requires the attacker to control (or observe) at least one shop that has the target app installed, and to be able to produce or capture a webhook whose raw body is identical or predictable across shops (many webhook topics send minimal or content-independent bodies, e.g., `{}`, or `shop/redact`/`customers/redact` GDPR payloads which have well-known, near-fixed shapes). No knowledge of the app's `client_secret` is required — this is exactly the "unprivileged internet user" analog: the attacker only needs to be a legitimate, unprivileged install of the same app on their own store, then forges the header on a replayed request to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified signable content, or otherwise reject/re-derive the shop identity from a source that is itself authenticated. Concretely:
- Change `Webhooks::Request#to_signable_string` (or add a secondary check) to incorporate the `shop-domain` header into what's validated, or
- Have `Registry.process` cross-check `request.shop` against the shop associated with the specific webhook subscription/registration (e.g., verify the webhook was actually registered for that shop, using Shopify's `webhook_id` lookup) before invoking the handler, and
- Document clearly that `to_signable_string` currently only covers the body, so app authors relying solely on `Utils::HmacValidator.validate` should not treat `shop` as authenticated without additional verification.

### Proof of Concept
1. App has a single `client_secret` shared by all installs; Shop A and Shop B both install it.
2. Shopify sends Shop A a webhook of a topic with a fixed/near-empty body, e.g. `raw_body = "{}"`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of "{}">`
   - `x-shopify-shop-domain: shop-a.myshopify.com`
3. Attacker (an operator of Shop A) captures this raw body and HMAC header (they can see their own store's webhook deliveries/logs, or simply trigger an event that produces `{}`).
4. Attacker sends a forged HTTP request to the app's webhook endpoint reusing the same `raw_body` and `x-shopify-hmac-sha256`, but sets:
   - `x-shopify-shop-domain: shop-b.myshopify.com` (the victim)
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully (all required headers present).
6. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, "{}")` — identical to the original — and returns `true`.
7. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "shop-b.myshopify.com", body: {}, ...))`, causing the app to act on Shop B's tenant data using an event the attacker fabricated, despite never possessing the app's `client_secret`.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
