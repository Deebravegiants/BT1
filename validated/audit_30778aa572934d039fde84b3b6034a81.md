### Title
Webhook HMAC verification signs only the raw body, not the shop-domain header, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, and `Request#to_signable_string` returns only `@raw_body` as the signed payload. The `shop` value that is subsequently trusted and forwarded to the app's `WebhookHandler` is read from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not part of the HMAC-signed material.

### Finding Description
`Request#to_signable_string` binds the HMAC exclusively to the raw request body: [1](#0-0) 

But `Request#shop` — the value the gem treats as the authenticated tenant identifier for the webhook — is pulled straight from a header that carries no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately constructs `WebhookMetadata` using the unauthenticated `request.shop` and hands it to the host app's handler: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `hmac_signed_bytes == bytes_that_determine_the_tenant`. Here, the HMAC is verified over `raw_body` only, while the tenant used downstream is `header["shop-domain"]`, which is disjoint from the signed bytes. Anyone who legitimately receives one Shopify-signed webhook for their own store (e.g., by installing the app on a free/dev shop and subscribing to any topic with a small/fixed body, or capturing a delivery for a topic whose body content is attacker-influenced, such as a `shop/redact` or `customers/redact` mandatory-compliance webhook) obtains a `(raw_body, hmac)` pair that is valid for that exact body — and remains valid for the exact same body no matter what `shop-domain` header value is attached, because that header is never covered by the signature.

### Impact Explanation
An external, unprivileged actor who controls a real Shopify store that has the app installed can capture one genuinely Shopify-signed webhook payload and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop. Because `HmacValidator.validate` only checks `raw_body` against the secret, the forged request passes verification and the app's handler executes attacker-supplied `body`/`topic` content while believing it originates from the victim's shop (`WebhookMetadata#shop`). Depending on how the host app uses `data.shop` (e.g., to look up the victim's session/access token and perform destructive or state-changing actions, such as data-erasure handling for `customers/redact`/`shop/redact`), this can produce cross-tenant data corruption or trigger privileged per-shop operations under a victim's identity — a cross-tenant access class of impact.

### Likelihood Explanation
Moderate-to-high for apps that trust `data.shop` from the handler without independently re-verifying tenancy (e.g., via a webhook_id lookup against Shopify or an out-of-band shop confirmation), since the gem provides no protection against shop-domain header spoofing beyond documenting it as a header value. The attacker needs only their own legitimate, HMAC-signed webhook deliveries from Shopify (attainable by installing the app on any store they control) plus the ability to send an arbitrary HTTP POST to the app's public webhook endpoint — no `api_secret_key`, access token, or privileged account is required.

### Recommendation
Include the shop domain (and ideally the topic and webhook id) in the value that is cryptographically bound to the request — either by having `Request#to_signable_string` incorporate `shop`/`topic`/`webhook_id` alongside the body where the calling application's threat model requires shop-binding, or, more robustly, by documenting/enforcing that `WebhookHandler` implementations must not treat `WebhookMetadata#shop` as authenticated and must independently confirm shop identity (e.g., cross-check against the shop associated with `webhook_id` via the Admin API) before performing any shop-scoped mutation.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com` and let it register for a webhook topic whose delivery body is attacker-influenced or fixed (e.g., `customers/redact` with a minimal/predictable JSON body).
2. Capture the legitimate delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(api_secret_key, B)` as verified by `HmacValidator.validate` against `Request#to_signable_string` == `B`), per `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb`.
3. Replay a new POST to the same app endpoint using the identical body `B` and identical `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which still passes because only `B` is checked; `WebhookMetadata.shop` is now `"victim.myshopify.com"`, and the host app's handler executes as if the (attacker-controlled) body originated from the victim shop, per `lib/shopify_api/webhooks/registry.rb:188-200`.

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
