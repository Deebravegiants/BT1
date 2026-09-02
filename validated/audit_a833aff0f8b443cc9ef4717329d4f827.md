### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator.validate` never covers the `shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` trusts that header as the tenant identity (`request.shop`) when dispatching to the app's handler, breaking the binding between "HMAC-authenticated bytes" and "shop the data is attributed to."

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only the raw body is signed. The `shop` accessor reads a separate, unsigned header: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.shop` to build the metadata passed to the app's handler: [3](#0-2) 

The equality that should hold is: `shop cryptographically bound by HMAC == shop used to attribute the webhook data (request.shop)`. In this implementation that equality never actually holds — the HMAC only proves "this body was signed with the app's client secret"; it proves nothing about which shop header should accompany it. Since a multi-tenant app's `client_secret` (and therefore HMAC key, via `Context.api_secret_key`) is identical across every shop that installs the app, any actor who installs the app on their own store can obtain a genuine `(raw_body, hmac)` pair from Shopify, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header value (e.g., a victim shop's domain). `HmacValidator.validate` will still succeed because it only recomputes the digest over the unchanged body: [4](#0-3) 

and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop: [5](#0-4) 

### Impact Explanation
This is a cross-tenant integrity issue: an unprivileged actor (one who merely installs the multi-tenant app on their own shop, gaining no special privilege) can cause the host application's webhook handler to process attacker-supplied data under a victim shop's identity. Depending on how the host app uses `data.shop` (routing to per-tenant records, keying database writes, replaying state), this can lead to cross-tenant data corruption or confusion — data attributed to shop B is actually attacker-controlled, sourced from shop A's install.

### Likelihood Explanation
Requires only that the attacker install the app on their own store (a normal, permission-less action available to anyone) and that the host app relies on `data.shop` from `ShopifyAPI::Webhooks::WebhookMetadata` for tenant attribution, as the gem's own documentation instructs (`docs/usage/webhooks.md`). No access to `api_secret_key`, tokens, or the victim's infrastructure is required. The only extra step is capturing/replaying an HTTP request with a modified header, which is trivial once the attacker controls their own valid webhook delivery.

### Recommendation
Include the shop identifier (and topic, api-version, webhook-id) inside the HMAC-signable content, or otherwise cryptographically bind the header-derived `shop` value to the signed payload, so `HmacValidator.validate` fails if the shop header is altered relative to what Shopify actually sent for that body. At minimum, document prominently that `data.shop` is unauthenticated and must not be used to key tenant-sensitive operations without additional verification (e.g., cross-checking against the shop associated with the specific webhook subscription/session).

### Proof of Concept
1. Attacker installs the target multi-tenant app on their own shop `attacker-shop.myshopify.com`, so the app registers a webhook (e.g., `orders/create`) for that shop.
2. Attacker triggers the event in their own shop, causing Shopify to POST a legitimate webhook to the app's endpoint with a valid `Shopify-Hmac-Sha256` header computed over `raw_body` using the app's shared `client_secret`.
3. Attacker captures `raw_body` and the valid `hmac` value, then re-sends the identical body/HMAC pair to the app's webhook endpoint, replacing the `Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) calls `HmacValidator.validate(request)`, which recomputes the digest only over `raw_body` — validation succeeds unchanged.
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using the forged `shop` header, and the host app's handler processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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
