The docs at `docs/usage/webhooks.md:125` explicitly promise: "This will verify the request did indeed come from Shopify" — but the `shop` field delivered to the handler is not actually covered by that verification, only the raw body is. This confirms the finding is a genuine gap in the gem's own documented guarantee, not a misuse by the host app.

### Title
Webhook shop-domain header is trusted by the registry without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, excluding the `shop` (and `topic`/`webhook_id`/`api_version`) values read from HTTP headers. `Utils::HmacValidator.validate` verifies only that string against the app's `client_secret`. `Registry.process` then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata`, which the docs (`docs/usage/webhooks.md`) instruct developers to use as the tenant identifier for scoping data/enqueued jobs.

### Finding Description
The binding that should hold is: `hmac == HMAC(secret, body || shop)`, i.e., every field the app relies on to route/scope the webhook should be bound to the signature. Instead the gem computes and checks: [1](#0-0) 

only over the raw body, while: [2](#0-1) 

reads `shop` from the `shopify-shop-domain`/`x-shopify-shop-domain` header independent of the signed content. `HmacValidator.validate_signature` confirms this — it only ever touches `to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC, then unconditionally trusts `request.shop`: [4](#0-3) 

Because the app's `client_secret` is the same for every shop that installs the app (it is not shop-specific), any body+HMAC pair that is valid for shop A's webhook is *also* a valid HMAC for the exact same body claimed to be from shop B — the signature says nothing about which shop it belongs to. An attacker who legitimately installs the app on their own store (an unprivileged internet user from the app's perspective, requiring no `api_secret_key`, access token, or privileged account) can capture one of their own genuine webhook deliveries (body + valid `x-shopify-hmac-sha256`) and replay that exact HTTP request to the app's webhook endpoint while only changing the `x-shopify-shop-domain` header to a victim shop's domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is untouched), and `Registry.process` will hand the handler `WebhookMetadata` with `shop` set to the victim's domain and attacker-controlled `body`.

### Impact Explanation
This breaks the cross-tenant boundary the gem's documentation promises to enforce: "`Registry.process`... will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and the docs tell developers to key their tenant-scoped side effects (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`, `docs/usage/webhooks.md:26`) directly off `data.shop`. Since `shop` is never part of the signed payload, any installer of the app can forge webhook events attributed to any other merchant shop with attacker-chosen JSON body content, letting them inject fabricated `orders/create`, `products/update`, GDPR, or other topic events into a victim tenant's data pipeline. This is a cross-tenant access vulnerability per the Critical impact category.

### Likelihood Explanation
Likelihood is high for any app that exposes a public webhook endpoint (the standard, documented integration pattern) and relies on `WebhookMetadata#shop` for tenant scoping, which is exactly what the gem's own usage docs instruct. The only prerequisite is that the attacker have installed the app on at least one shop they control (a normal, unprivileged flow) to obtain one valid signed body/HMAC pair, and be able to trigger a webhook event with attacker-influenced body content (e.g., naming a product/order field).

### Recommendation
Include the authenticated tenant identifier in the signed material, or otherwise cryptographically bind `shop` to the HMAC before trusting it. Concretely, `Request#to_signable_string` should incorporate `shop` (and ideally `topic`, `webhook_id`) into the signed string, or `HmacValidator`/`Registry.process` should independently confirm that the `shop` header corresponds to a shop with a known/registered webhook subscription (e.g., by validating against `webhook_id` looked up via the Admin API) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) with an order whose fields (e.g., `note`) contain attacker-chosen content.
2. Attacker captures the resulting HTTP POST: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(client_secret, B)` — a signature that is valid for the app's `client_secret` regardless of shop.
3. Attacker replays this exact request to the app's public webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header successfully (`lib/shopify_api/webhooks/request.rb:20-23`); `Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because it only checks `B` and `H` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to process attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
