### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing in `Webhooks::Registry.process` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC computed only over the raw request body, but then trusts a *separate, unauthenticated* HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`) as the tenant identity that gets handed to the app's webhook handler. This breaks the intended binding: `HMAC-verified bytes == identity used downstream`.

### Finding Description
`Webhooks::Request` implements `VerifiableQuery` with: [1](#0-0) 
so the *only* bytes covered by the HMAC are `@raw_body`.

The `shop` (tenant identity) is read from a plain header, entirely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` — the unauthenticated header value — to the app's handler as the authoritative tenant identity: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further verification: [4](#0-3) 

**Equality that should hold but doesn't:** `shop_bound_by_hmac == shop_used_by_handler`. In reality `hmac` binds only `raw_body`, while `shop` used by `Registry.process`/`WebhookMetadata` comes from an attacker-controlled header that is never part of `to_signable_string`.

**Attack path (unprivileged internet user with their own Shopify store/app install):**
1. Attacker owns Shop A, which has the target app installed, so Shopify legitimately sends the attacker's app-facing endpoint real webhooks for Shop A, each with a valid `x-shopify-hmac-sha256` computed over the body using the app's `client_secret`.
2. Attacker triggers an action in their own store that produces a webhook body they control the content of (e.g., renaming a product/order to attacker-chosen values), capturing `(raw_body, valid_hmac)` for that body.
3. Attacker resends this exact `(raw_body, hmac)` pair to the app's webhook endpoint, but overwrites the `x-shopify-shop-domain` header to Shop B's domain (a victim/other tenant).
4. `Utils::HmacValidator.validate(request)` still succeeds because it only checks the body against the HMAC — the header is irrelevant to the signature.
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-supplied header value ("Shop B"), and the app's `WebhookHandler#handle` executes business logic (e.g., updating stored data, triggering side effects, cache/database writes keyed by shop) attributing attacker-controlled content to Shop B.

### Impact Explanation
This is a cross-tenant data/identity confusion inside the gem's own webhook-processing pipeline: it lets one authenticated merchant (attacker) inject arbitrary payload content that the app will process under a different, unrelated shop's identity. Depending on what the host app's `WebhookHandler` does with `data.shop` (write to per-shop storage, trigger per-shop side effects, invalidate/replace stored settings, etc.), this can corrupt or exfiltrate another tenant's data/state — a cross-tenant access impact, entirely reachable through this gem's documented `Registry.process` API without needing the target's access token, `client_secret`, or any privileged credential.

### Likelihood Explanation
Any Shopify merchant can install the target app on their own store and thus legitimately receive real, validly-signed webhooks for arbitrary content they control. Forging the HTTP header on replay requires no cryptographic material and no special access — only the ability to send an HTTP request to the app's public webhook endpoint, which is by definition internet-reachable. The only prerequisite is that the app's handler logic keys behavior off `WebhookMetadata#shop`, which is exactly what this field exists for.

### Recommendation
Include the shop-identifying header(s) (and ideally topic/webhook-id) in the HMAC signable string, or otherwise verify the header value against an independently-authenticated source before trusting it — e.g., require the caller to look up the shop from a value that is itself covered by the signature, or bind and verify `shop-domain` inside `to_signable_string` in `lib/shopify_api/webhooks/request.rb` so `Utils::HmacValidator.validate` fails if the header is altered post-signing.

### Proof of Concept
```
# Attacker installs app on Shop A, triggers a webhook with attacker-chosen body content,
# capturing a valid (raw_body, hmac) pair signed by Shopify using the app's real client_secret.

POST /webhooks HTTP/1.1
x-shopify-topic: products/update
x-shopify-hmac-sha256: <valid HMAC computed over raw_body using app's client_secret>
x-shopify-shop-domain: shop-b-victim.myshopify.com   # <-- forged, arbitrary value, NOT covered by HMAC
x-shopify-api-version: 2024-01
x-shopify-webhook-id: attacker-chosen-id

<raw_body captured from a real Shop-A webhook, fully attacker-controlled content>
```
`Utils::HmacValidator.validate(request)` at `lib/shopify_api/webhooks/registry.rb:190` returns `true` because it only checks `raw_body` against the hmac; `Registry.process` then calls the handler with `shop: "shop-b-victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), executing the app's per-shop logic under the wrong tenant.

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
