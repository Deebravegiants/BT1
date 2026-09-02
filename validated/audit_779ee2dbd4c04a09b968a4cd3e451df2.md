Confirmed. The `shop` field passed to app handlers is derived purely from the `shopify-shop-domain` HTTP header and is never included in the HMAC-signed bytes.

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (tenant identifier) is read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header. `Registry.process` validates the HMAC over the body only, then forwards `request.shop` straight into `WebhookMetadata`, which host apps use to attribute the webhook to a merchant/tenant.

### Finding Description
`HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string`, which for `Request` is `@raw_body` alone: [1](#0-0) 
The `shop` accessor is derived independently, purely from a header value with no cryptographic binding to the signature: [2](#0-1) 
`HmacValidator.validate_signature` confirms the check is over `to_signable_string` (the body) and the `hmac` header only — nothing else: [3](#0-2) 
`Registry.process` performs the HMAC check and then trusts `request.shop` to build the `WebhookMetadata` that is handed to the app's business logic: [4](#0-3) 

The intended identity binding is: **`shop` (attributed tenant) == `shop` whose secret produced the HMAC over this exact payload**. Because `shop` is excluded from the signed bytes, this equality is never enforced — the gem verifies "these bytes came from someone holding `api_secret_key`" but not "these bytes are associated with *this* shop." Any merchant that has legitimately installed the app (an ordinary, unprivileged action for any Shopify developer/store owner) receives real webhooks with valid HMACs computed only over their own body content. That merchant can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. The signature still validates (it never covered the shop), so `Registry.process` accepts the request and invokes the handler with `WebhookMetadata#shop` set to the victim's domain and attacker-controlled `body`/`topic`.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: an attacker holding valid webhook material from their own tenant can inject data attributed to a different, victim tenant's shop into the host application. If the host app uses `WebhookMetadata#shop` (as documented) to look up per-shop sessions/records and drive side effects (e.g., updating inventory, orders, subscription state, deleting resources) keyed by that shop, this is cross-tenant data corruption/injection — one of the explicitly in-scope Critical impacts (cross-tenant access).

### Likelihood Explanation
Likelihood is bounded by needing at least one valid `(raw_body, hmac)` pair, which any merchant who installs the app already possesses for their own real webhooks — no `api_secret_key` or access-token theft required, and no reliance on the host app misusing the API contrary to documentation (the documented flow in `docs/usage/webhooks.md` is exactly to trust `Registry.process`'s HMAC check and consume `data.shop`).

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) header value in the signable material verified by `HmacValidator`, or otherwise cryptographically bind the shop domain to the signature (e.g., verify shop against a value independently obtained via a per-shop registration record rather than trusting the header verbatim).

### Proof of Concept
1. Install the target app on an attacker-controlled dev store `attacker.myshopify.com`; trigger any registered webhook topic (e.g. `orders/create`) to receive a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's real `api_secret_key`.
2. Replay that exact `raw_body` and `hmac` header to the app's public webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `raw_body` against `hmac`.
4. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` line 190-198 dispatches to the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the host app to process attacker-supplied data as if it originated from the victim shop.

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
