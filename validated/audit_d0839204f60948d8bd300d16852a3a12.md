### Title
Webhook `shop` identity is not bound by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs (and the registry verifies) only the raw request body, while the `shop` field that identifies the tenant a webhook belongs to is read from an unauthenticated header and handed to the app's handler as trusted tenant identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over `raw_body` only) and, once that check passes, immediately forwards `request.shop` to the app's handler as the authoritative tenant identifier: [3](#0-2) 

The HMAC secret (`api_secret_key`) is a single value shared by the app across *every* installed shop — it is not shop-specific: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified bytes == raw_body` but `WebhookMetadata.shop == unauthenticated header value`, rather than `WebhookMetadata.shop == shop bound to the signed payload`. An unprivileged internet user who controls any shop capable of installing the app (e.g., their own dev store) can subscribe to a webhook topic, capture a legitimate `(raw_body, hmac)` pair produced by Shopify for their own shop, and replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. Because `Utils::HmacValidator.validate` only checks the body bytes against the shared `api_secret_key` — not the shop header — the check passes for any shop of that app, and the forged `shop` value flows unchecked into `WebhookMetadata` and the developer's `handle` callback.

### Impact Explanation
This is a cross-tenant identity-binding failure: the gem hands the app a `shop` value in `WebhookMetadata` that is asserted to be authenticated (having passed HMAC validation) but is actually attacker-controlled. Any app logic that keys off `WebhookMetadata#shop` to select the tenant's session/data context (a common and encouraged pattern, since `Registry.process` is the gem's blessed webhook-processing entrypoint) can be made to apply data/actions belonging to one shop under another shop's identity — a cross-tenant access impact.

### Likelihood Explanation
The attacker only needs the ability to install the app on/subscribe a webhook for a shop they control (a normal, unprivileged action available to any Shopify merchant/dev-store owner) and the ability to send an arbitrary HTTP request with a forged header to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — the shared per-app secret’s output over the captured body is reused verbatim.

### Recommendation
Bind the shop identity into the verified material, e.g. include `shop-domain` (and ideally `webhook-id`) in `to_signable_string`, or otherwise validate that `request.shop` matches the shop the receiving endpoint expects/owns before dispatching to `handler.handle`, rather than trusting the unauthenticated header value once the body-only HMAC succeeds.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets the app register a webhook (e.g. `orders/create`).
2. Attacker triggers the webhook and captures Shopify's genuine POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)` per `lib/shopify_api/utils/hmac_validator.rb`).
3. Attacker resends the request to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against `H` using the app's single `api_secret_key` — this succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop = "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198`) and passed to the app's handler, which processes attacker-controlled webhook content under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
