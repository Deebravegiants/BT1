### Title
Webhook `shop` identity is trusted for tenant routing while excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` field it hands to registered webhook handlers comes from an unauthenticated header (`x-shopify-shop-domain` / `shopify-shop-domain`). The equality that should hold is: `shop bound by HMAC == shop delivered to handler`. In this gem it instead holds `shop bound by HMAC == ∅` (the HMAC binds only the body) while `shop delivered to handler == header value`, so the tenant identifier used by the app is not part of what `Utils::HmacValidator.validate` actually verifies.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`HmacValidator.validate_signature` recomputes the HMAC over exactly that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

Meanwhile `shop` is read straight from the (unsigned) `shop-domain` header with no cross-check against the HMAC-covered content: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately dispatches to the app's handler using that same unauthenticated `request.shop` value as the tenant identifier: [4](#0-3) 

Because the HMAC only proves "this body was produced with knowledge of `api_secret_key`," not "this body belongs to shop X," any request that reuses a previously-valid `(body, hmac)` pair — for example a legitimately-captured webhook that the attacker's own store received — will still pass `HmacValidator.validate` even if the `x-shopify-shop-domain` header is changed to name a different shop. The library performs no additional binding (e.g., re-deriving/checking the shop against the HMAC, or against a known list of shops the app is installed on) before handing `shop` to the handler.

### Impact Explanation
Cross-tenant data confusion / cross-tenant access: applications built on this gem routinely use `WebhookMetadata#shop` (or the block’s `shop`) as the primary key to decide which merchant's records to update/delete/create in response to a webhook (this is the documented purpose of the `shop` field returned from `Registry.process`). If the shop field can be forged independently of the signed body, an attacker who can obtain one authentic `(body, hmac)` pair (trivially, from their own shop's webhooks) can replay it against the app's public webhook endpoint with a spoofed `x-shopify-shop-domain` header, causing the host application to attribute another shop's data/action to the attacker-chosen tenant. This crosses the tenant boundary the HMAC is meant to enforce.

### Likelihood Explanation
Requires only an unprivileged internet user who can send HTTP requests to the app's public webhook endpoint and who has previously received (or can obtain) any one legitimately-signed webhook body/HMAC pair for the configured `api_secret_key` (e.g., from their own installed shop). No access token, `client_secret`, or privileged account is needed — this is purely a header vs. signed-body mismatch reachable by any caller of the webhook endpoint. The exploitability ultimately depends on how the host app uses `shop`, but the gem itself provides no protection or documentation warning that `shop` is unauthenticated relative to the HMAC, and `Registry.process` forwards it unconditionally.

### Recommendation
Bind `shop` into the material verified by `HmacValidator`, or otherwise have `Registry.process` cross-validate `request.shop` against an application-registered/trusted shop list before dispatch. At minimum, document prominently in `Request`/`Registry` that `shop` is not covered by the HMAC and must not be trusted as an authenticated tenant identifier without additional verification (e.g., confirming the shop has an active, previously-established session/installation record) before using it for tenant-scoped operations.

### Proof of Concept
1. App installs/receives one legitimate webhook for `shop-a.myshopify.com` with body `B` and valid header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker resends the identical request to the app's webhook endpoint but changes only `x-shopify-shop-domain` to `shop-b.myshopify.com` (a different tenant the attacker does not control).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [1](#0-0)  and succeeds because the body/HMAC pair is still valid.
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "shop-b.myshopify.com", body: B, ...)` [5](#0-4) , causing the app to process shop A's payload under shop B's identity.

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
