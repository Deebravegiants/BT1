### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` accepts a webhook once `Utils::HmacValidator.validate(request)` succeeds, and then hands `request.shop` straight to the app's handler as the authenticated tenant identifier. The HMAC, however, is computed only over the raw request body (`to_signable_string` returns `@raw_body`), never over the `shop-domain`/`x-shopify-shop-domain` header. This breaks the equality the caller assumes: `shop used for tenant routing == shop the HMAC vouches for`. In reality, `shop the HMAC vouches for == nil` (the HMAC vouches only for the body bytes), while `shop used for tenant routing == attacker-suppliable header value`.

### Finding Description
`ShopifyAPI::Webhooks::Request` reads the shop from a header: [1](#0-0) 

Its `to_signable_string`, which is what `HmacValidator` HMACs and compares against the `hmac-sha256` header, is exclusively the raw JSON body: [2](#0-1) 

`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over that signable string with `Context.api_secret_key` and compares it (constant-time) to the received `hmac` value — it never incorporates `shop`, `topic`, or `webhook-id`: [3](#0-2) 

`Registry.process` raises `InvalidWebhookError` only if this body-only HMAC fails, then immediately forwards `request.shop` (and `request.topic`, `request.webhook_id`) to the app's handler as if these were also authenticated: [4](#0-3) 

Because `api_secret_key` is a single per-app secret shared across every merchant/shop that installs the app (not a per-shop secret), any merchant who has a real, valid webhook delivery from Shopify for their own shop possesses a body + HMAC pair that is valid for that app's secret regardless of which shop the body nominally describes. Since the `shop-domain` header sits outside the signed content, that same attacker can resend the identical `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g. a victim shop). `HmacValidator.validate` still returns `true` because it only re-hashes the body, so `Registry.process` accepts the request and calls the handler with the attacker-chosen `shop` value bound to the attacker's own (legitimately-signed) body content.

### Impact Explanation
This crosses a tenant boundary: the host application's webhook handler receives data it will treat as originating from, and scoped to, a specific shop (`WebhookMetadata#shop` from `data.shop`), but the gem provides no cryptographic guarantee that the claimed shop is the shop that actually generated the body. An attacker who is a legitimate installer of the app on their own store can inject events/data that the app processes as if they came from a different, victim tenant — i.e., cross-tenant access/spoofing, satisfying the Critical impact bar in this context (cross-tenant access enabled purely through this gem's webhook validation logic).

### Likelihood Explanation
Requires only: (1) the attacker be an app user/merchant able to receive one legitimate webhook for their own shop (trivial — install the app, trigger any subscribed event), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is inherent to any internet-reachable webhook receiver. No access token, `api_secret_key`, or privileged account is needed — the whole point is that the shared secret's validity is reused across the *header* field it doesn't cover.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the value that is HMAC-verified, or otherwise independently verify that `request.shop` corresponds to a shop with an active, stored session/installation known to the app before dispatching to handlers — i.e., `Utils::HmacValidator.validate` (or `Registry.process`) should not allow header-derived identity fields to be treated as authenticated when only the body is covered by the signature. At minimum, `Registry.process`/`WebhookMetadata` documentation should make explicit that `shop` is unauthenticated header data and must be cross-checked by the host app against its own session store before use, since the library currently returns it alongside data that appears to have passed a security check (`InvalidWebhookError` gate).

### Proof of Concept
1. App is installed on `attacker.myshopify.com`; attacker triggers a subscribed webhook event and captures the raw POST Shopify sends to the app: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B` under the app's shared `api_secret_key`), header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker crafts a new POST to the same app webhook endpoint with the identical body `B` and identical `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` (`B`) only, matches `H`, returns `true`. [5](#0-4) 
4. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...))`, i.e. the app processes attacker-controlled body content tagged as belonging to `victim.myshopify.com`.

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
