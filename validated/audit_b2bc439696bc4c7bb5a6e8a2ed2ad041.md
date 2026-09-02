### Title
Webhook shop attribution is trusted from an unauthenticated header, breaking `shop-domain == HMAC-covered data` binding — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verification performed by `Utils::HmacValidator.validate` covers exclusively the JSON body bytes. The `shop-domain`, `topic`, `webhook_id`, and `api-version` values are read straight from HTTP headers and are never part of the signed material, yet `Registry.process` forwards `request.shop` unchanged into `WebhookMetadata` and hands it to the app's handler as the authenticated tenant identifier.

### Finding Description
The binding that should hold is: `shop attributed to a webhook == shop bound to the HMAC signature`. Instead the code produces:
`shop attributed to a webhook (from header) != shop bound to the HMAC signature (never present in signed bytes)`.

- `Request#to_signable_string` [1](#0-0) : signs only `@raw_body`.
- `Request#shop` [2](#0-1) : pulled from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not covered by the signature above.
- `HmacValidator.validate_signature` [3](#0-2)  only checks `verifiable_query.to_signable_string` (i.e., the body) against the HMAC, so it can succeed for any header combination.
- `Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build `WebhookMetadata` passed to the merchant's handler: [4](#0-3) .

Because a public app's webhook signing secret (`api_secret_key`) is shared across every shop that installs the app, an unprivileged holder of one legitimate installation (their own shop) can obtain a genuinely-signed `(raw_body, hmac)` pair for their own webhook deliveries without ever needing the secret itself — Shopify computes and sends it to them. That attacker can then replay the identical body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header naming a victim shop. Because the header is outside the signed bytes, `HmacValidator.validate` still returns `true`, and `Registry.process` will happily hand the app's handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant/authentication boundary the gem is supposed to enforce for webhook delivery: any handler logic that uses `WebhookMetadata#shop` to decide which merchant's data store to write to, which access token/session to look up, or which merchant-scoped side effect to trigger, can be made to act on behalf of a different, victim tenant using only a self-obtained, validly-signed payload. This matches the "cross-tenant access" criterion for High/Critical impact in the rules, since the crossing occurs purely through data this library asserts is authenticated (`request.shop` from a "validated" webhook).

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop (a normal, unprivileged action available to any merchant/developer), (2) capturing one legitimate webhook delivery for that shop (freely provided by Shopify once a topic is subscribed), and (3) replaying it with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged credential is needed — the attacker only ever uses material Shopify itself delivered to their own, legitimately-installed shop.

### Recommendation
Bind the shop identity to the signed payload instead of trusting an unauthenticated header:
- Include `shop-domain` (and ideally `topic`, `webhook_id`, `api-version`) in `to_signable_string`, or
- Cross-check `request.shop` against an independently-authenticated source (e.g., the webhook subscription's registered callback shop, or an out-of-band shop confirmation) before it is used to select tenant-scoped resources, and document clearly that `WebhookMetadata#shop` must not be trusted as authenticated by HMAC alone in `Registry.process` / `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify delivers a legitimate request with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Attacker replays this exact `(B, H)` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)` and finds it equal to `H` — validation passes [5](#0-4) .
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "victim-shop.myshopify.com"` [6](#0-5) , and the app's handler executes tenant-scoped logic believing the (attacker-supplied) body genuinely belongs to the victim shop.

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
