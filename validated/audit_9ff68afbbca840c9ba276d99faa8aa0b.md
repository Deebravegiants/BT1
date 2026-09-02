### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant shop-spoofing replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, but `to_signable_string` — the data that `HmacValidator` actually verifies — only ever returns the raw request body. The `shop` header is never part of the signed material, so any attacker who possesses one valid `(body, hmac)` pair for their own store can replay it against the same webhook endpoint while substituting an arbitrary `shop` header value, and the signature will still validate.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an attacker-controllable HTTP header with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` to build `WebhookMetadata` that is handed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `hmac == HMAC(secret, body ‖ shop)`, i.e. the verified bytes should equal the bytes the application acts on (body **and** shop). Instead the gem verifies `hmac == HMAC(secret, body)` while acting on `(body, shop)` where `shop` is unauthenticated. Concretely: `HmacValidator.validate` checks `computed_signature == received_signature` using only `verifiable_query.to_signable_string` (the body) — [4](#0-3)  — while `Registry.process` uses `request.shop` from the unsigned header to populate the metadata delivered to the host app's handler.

An unprivileged attacker who legitimately controls any Shopify store (e.g., a free development store) can install the target app (or intercept/observe their own genuine webhook deliveries, which are always sent with a valid HMAC for their shop and body), then resend that exact `(raw_body, hmac-sha256 header)` pair to the app's webhook endpoint while overwriting only the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because the signed bytes (raw body) are unchanged, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim's shop.

### Impact Explanation
Any host application built on this gem that uses `WebhookMetadata#shop` (or `Request#shop`) to decide which merchant/tenant record to update — which is the documented and expected usage pattern for webhook handlers — can be tricked into writing or acting on attacker-supplied data under a different, victim tenant's identity. This is a cross-tenant confusion/injection primitive achieved purely by forging an HTTP header, without needing the app's `client_secret`, any access token, or the victim's credentials.

### Likelihood Explanation
Likelihood is realistic: obtaining a valid `(body, hmac)` pair only requires installing the target app on any store the attacker controls (a normal, unprivileged, self-service action) and capturing one webhook delivery. Replaying it with a modified `shop` header requires no cryptographic secret and no interaction with the victim.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signed material verified against Shopify's HMAC, or, if Shopify's contract does not sign these headers, have the gem independently validate that the `shop` header corresponds to a known/authorized installation for this app (e.g., cross-check against an existing offline session for that shop) before constructing `WebhookMetadata`, and document that `shop` is untrusted unless such a check is performed by the host app.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any webhook (e.g., `orders/create`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header value `H` (valid because Shopify itself signs `B` with the app's real secret).
2. Attacker sends a new POST request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - `X-Shopify-Topic`/`X-Shopify-Webhook-Id`: unchanged or attacker-chosen (also unsigned, per `to_signable_string`)
3. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC solely over `@raw_body` and matches `H`, so validation passes: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...)`, causing the host app to process attacker-chosen data as if it came from `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
