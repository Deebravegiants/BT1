### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the request body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC before dispatching it to the app's handler, but the HMAC only signs the raw request body — it does not cover the `shop` value that the handler is told to trust.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header via `shopify_header("shop-domain")`. [1](#0-0) 

`Registry.process` validates only that `Utils::HmacValidator.validate(request)` succeeds, and if so, dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the app's registered handler, treating `request.shop` as authenticated tenant identity. [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC purely from `verifiable_query.to_signable_string` (the raw body) and the app's `api_secret_key`, so the digest never binds to the `shop-domain` header at all. [3](#0-2) 

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. In this implementation the equality is broken: the HMAC authenticates `{raw_body}` under the shared `api_secret_key`, while the `shop` field that flows into `WebhookMetadata` and ultimately into the host application's tenant-scoped logic (`docs/usage/webhooks.md` shows `data.shop` used directly to key persisted work) is taken from an unsigned header. [4](#0-3) 

Because `api_secret_key` is the single shared app secret used for **every** installed shop (not a per-shop key — see `Context.api_secret_key` used identically in `HmacValidator.validate`), any shop that has installed the app can legitimately receive a Shopify-signed webhook body+HMAC pair for its own data, then replay that exact body to the same handler endpoint while substituting the `shopify-shop-domain` header to name a different (victim) shop. `HmacValidator.validate` still returns `true` because the digest is computed over the body only, so `Registry.process` proceeds and hands the handler a `WebhookMetadata` claiming the victim shop’s identity for attacker-controlled body content.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: it allows an authenticated-but-unprivileged merchant (any shop that installed the app) to make the host application process/store attacker-supplied payload data under another shop's identity — a cross-tenant data-confusion/injection primitive reachable purely from having installed the app once, with no access to `api_secret_key`, access tokens, or privileged accounts.

### Likelihood Explanation
Any shop that installs the app receives genuine Shopify webhooks (valid body + HMAC) for events it triggers on its own store — this is the normal, unprivileged experience of any merchant. Forging the replay only requires re-POSTing the captured body to the app’s public webhook endpoint with a different `shop-domain` header value; no cryptographic secret is needed since the header isn’t part of the signed material.

### Recommendation
Bind the trusted `shop` identity to the signed payload: either include the shop domain in the HMAC-signed material (matching Shopify's documented webhook signing, which the app should cross-check against the shop domain it registered the webhook for), or require the host app to validate `request.shop` against a shop it actually has an active session/webhook registration for before invoking the handler, and document this requirement clearly since currently the gem's own `docs/usage/webhooks.md` example passes `data.shop` straight through as trusted.

### Proof of Concept
1. App AppX shares one `api_secret_key` across all installs.
2. Malicious merchant "attacker.myshopify.com" installs AppX and registers for `orders/create`. Shopify sends AppX's webhook endpoint a legitimately signed webhook: body `B`, header `shopify-shop-domain: attacker.myshopify.com`, and `shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker captures this raw request (they control the traffic to their own installed webhook receiver / can trivially trigger and observe it) and replays it to AppX's webhook endpoint, keeping body `B` and the HMAC header identical, but changing the header to `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` reads the unchanged HMAC header; `to_signable_string` returns the unchanged body `B`; `HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches, returning `true`.
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process/store attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
