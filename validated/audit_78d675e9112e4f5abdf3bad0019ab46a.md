### Title
Webhook `shop` (tenant identifier) is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signable string from the raw body only, while the `shop` (and `topic`) are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then passes the header-derived `shop` value straight to the app's handler as a trusted tenant identifier, without binding it to the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `Request#shop` is pulled directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding: [2](#0-1) .

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` (i.e., the raw body) using `Context.api_secret_key`, which is the single `client_secret` shared by the app across every installed shop/tenant: [3](#0-2) .

`Registry.process` only checks this body HMAC, then forwards the *unauthenticated* `request.shop` (and `request.topic`) to the handler as if verified: [4](#0-3) .

The identity binding that should hold is: `HMAC-verified bytes == bytes used to determine which tenant/shop the webhook is attributed to`. Because the HMAC only covers the JSON body, and Shopify webhook bodies for most topics do not embed a self-authenticating shop domain that the host app cross-checks, `shop` is effectively "bytes verified vs. bytes parsed" — the header is parsed and trusted, but never verified.

Since `Context.api_secret_key` is the app's single `client_secret`, valid HMACs are computed identically for webhooks originating from *any* shop that has installed the app. Any unprivileged user can install the app on their own (e.g., free development) store — a normal, unprivileged action — and thereby receive a genuinely Shopify-signed webhook (`raw_body` + valid `x-shopify-hmac-sha256`) for their own shop. They can then replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept it (the HMAC over the body still matches), and the handler will receive `WebhookMetadata` with `shop` set to the attacker-chosen victim domain: [5](#0-4) .

The gem's own documented usage pattern explicitly treats `data.shop` as the trusted tenant key for downstream processing (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), confirming that `shop` is expected to be authoritative: [6](#0-5) .

### Impact Explanation
This breaks the equality `verified-signer-identity == attributed-tenant-identity`, letting one tenant (shop) forge an event that a well-behaved host app will attribute to a *different* tenant. Depending on how the host app's handler uses `data.shop` (e.g., to key session/database lookups, apply webhook payloads, or trigger mutating background jobs against "that shop's" data), this results in cross-tenant data confusion/corruption — a Critical-class cross-tenant access issue per the scope's impact list, achievable by an unprivileged actor who only needs to install the app on their own store (no access token, no `api_secret_key` knowledge, no privileged account required).

### Likelihood Explanation
Any developer/merchant can freely install a public app (development stores are free and require no special privilege), obtain a legitimately signed webhook for a topic they control (e.g., `app/uninstalled`, `orders/create` in their own store), and replay the body + HMAC with a forged `shop` header to the app's public webhook endpoint. The gem provides no mechanism to bind `shop` to the signed content or to cross-check it against the shop that owns the webhook subscription, so exploitation only depends on the host app trusting `data.shop`, which is the pattern the gem's own docs recommend.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signable content verified against the HMAC, or independently corroborate the header-provided `shop` (e.g., by looking up the webhook subscription/registration owner via `webhook_id` through the Admin API) before trusting it in `WebhookMetadata`. At minimum, document prominently that `data.shop` is not covered by Shopify's HMAC and must not be trusted as a tenant key without additional verification.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store `attacker.myshopify.com`.
2. Trigger a webhook (e.g., `orders/create`) and capture the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify — this HMAC is valid because it's computed with the app's single shared `client_secret`.
3. Replay the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only checks `to_signable_string` (the raw body) — see [1](#0-0)  and [7](#0-6) .
5. The handler is invoked with `WebhookMetadata(shop: "victim.myshopify.com", ...)`, causing the host app to process attacker-controlled webhook content under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
