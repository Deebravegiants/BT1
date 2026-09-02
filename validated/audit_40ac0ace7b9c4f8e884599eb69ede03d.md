### Title
Webhook `shop` identity is not bound by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC verified by `Utils::HmacValidator` covers the webhook payload but never the `shop` field the library extracts from the `X-Shopify-Shop-Domain` header. `Registry.process` trusts that header value as the authoritative tenant identifier when dispatching to the app's handler, so the shop binding used by the application is not the shop binding verified by the signature.

### Finding Description
`Request#shop` is derived purely from an HTTP header: [1](#0-0) 

The HMAC signable string, however, is only the raw body — headers (including `shop-domain`) are excluded from what's signed: [2](#0-1) 

`HmacValidator.validate` computes/compares the signature strictly against `to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` validates the HMAC and, upon success, immediately hands `request.shop` (the unauthenticated header value) to the app's handler as the tenant identifier, with no cross-check that this shop is the one Shopify actually signed the payload for: [4](#0-3) 

This breaks the intended identity binding: `shop_used_by_handler (Request#shop, header)` should equal `shop_bound_by_hmac (Auth::Oauth::AuthQuery`-style signed field)`, but here the HMAC binds only the body, not the shop. Any party who can obtain one genuine Shopify-signed webhook body/HMAC pair for their own shop (e.g. by operating their own store and installing the app) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. The signature still validates (it never covered the header), so the app processes attacker-supplied event data under the identity of an arbitrary victim shop.

### Impact Explanation
This is a cross-tenant identity-confusion vector: the app-level handler (which typically uses `WebhookMetadata#shop` to scope database writes, cache invalidation, uninstall/redact flows, etc.) will act on a shop it never actually received a signed event for. Depending on how the host app uses the `shop` field (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`), this can drive cross-tenant data corruption, spurious redaction/uninstall processing for a victim shop, or data leakage tied to the wrong tenant — satisfying the cross-tenant access impact bar.

### Likelihood Explanation
Requires only that the attacker control one legitimate shop/installation to obtain a validly-signed webhook (body + HMAC) from Shopify, plus the ability to POST to the app's public webhook endpoint with a modified header — no access to `api_secret_key` or any Shopify-internal secret is needed. This is within reach of any unprivileged developer/merchant who installs the app on their own test store.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated, or independently verify that `request.shop` matches a shop known to have installed the app / matches the session associated with the topic, before dispatching to handlers. At minimum, incorporate the `X-Shopify-Shop-Domain` header into `to_signable_string` so the HMAC binds shop identity, consistent with how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` for the OAuth callback.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook topic whose payload they can influence in content (e.g., a topic with attacker-controlled resource fields). Shopify delivers a request with a valid `X-Shopify-Hmac-Sha256` computed over the raw body via the app's shared `api_secret_key`.
2. Attacker captures the raw body and the `X-Shopify-Hmac-Sha256` value.
3. Attacker crafts a new HTTP POST to the app's webhook endpoint using the *same* raw body and HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `to_signable_string` (the unmodified body) against the HMAC — validation succeeds: [4](#0-3) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, processing it as if it were a legitimate event for the victim shop.

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
