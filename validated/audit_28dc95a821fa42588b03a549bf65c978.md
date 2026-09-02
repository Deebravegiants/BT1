### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then forwards the *unauthenticated* `shop` header value to the host application's webhook handler as the trusted tenant/session key. This breaks the identity binding `authenticated_bytes == acted_upon_identity`, because the byte range verified by the HMAC (`raw_body`) is not the same as the field the app uses to select which shop's data to act on (`shop`).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it verifies the body bytes, never the shop header: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately constructs `WebhookMetadata` using `request.shop` — the unauthenticated header — as the tenant identity handed to the host app's handler: [4](#0-3) 

Because the app's `client_secret` (the HMAC key) is shared across every shop that has the app installed, any merchant who installs the app can obtain a genuinely-signed `(raw_body, hmac)` pair for their own shop (e.g. by triggering `orders/create` on their own store and capturing the webhook Shopify sends). That merchant can then replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body/HMAC pair is valid), but `Registry.process` passes the attacker-chosen `shop` value into `WebhookMetadata`, which host applications use as the session/tenant key to decide whose data to create, update, or act upon. This is exactly the binding gap called out in the rules: "a field acted on but not covered by the HMAC" / "a shop authenticated versus the shop stored as a session key."

### Impact Explanation
This allows an unprivileged, arbitrary internet user (any merchant who can install the app) to make the host application believe attacker-controlled webhook data belongs to a different, victim tenant (shop). Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g., as a lookup/session key to fetch that shop's access token, write records, or trigger shop-scoped side effects), this results in cross-tenant data corruption/confusion — meeting the Critical bar of "cross-tenant access."

### Likelihood Explanation
Likelihood is non-trivial but requires the attacker to be a legitimate installer of the target app (to obtain a validly-signed webhook for the shared `client_secret`) and to know/guess a victim shop's `.myshopify.com` domain (which is often discoverable/public). No access token, `api_secret_key`, or privileged credential is required — only replay of an intercepted, genuinely-signed webhook with a modified header, which any installer of the app can do against the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`, `api_version`, `webhook_id`) values into the HMAC-signed content, or otherwise verify that the `shop` header matches the shop encoded in a value the HMAC actually covers, before trusting it as the tenant key in `WebhookMetadata`. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate all header fields that downstream code treats as trusted identity, not just the raw body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — both are valid for the app's shared `client_secret`.
3. Attacker replays this exact request to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: request.shop, ...)` with `shop == "victim.myshopify.com"` and hands the attacker's body/topic to the host app's handler as if it originated from the victim shop (`lib/shopify_api/webhooks/registry.rb:188-200`).

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
