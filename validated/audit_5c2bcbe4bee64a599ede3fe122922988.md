### Title
Webhook `shop` Identity Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. Because the header is not part of the signed bytes, an attacker who possesses one valid (body, HMAC) pair from a webhook legitimately sent to their own tenant can substitute the `shop-domain` header to point at a different (victim) shop and the signature will still validate, causing the app's webhook handler to process the payload under the wrong tenant's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value used downstream for tenant identification is pulled straight from the (unsigned) `shopify-shop-domain` header, independent of the HMAC-covered content: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which recomputes the signature over `to_signable_string` (the raw body only) and compares it to the `hmac-sha256` header — it never binds the `shop-domain` header into the signed material: [3](#0-2) [4](#0-3) 

The identity binding that should hold is:
`bytes verified by HMAC == bytes used to determine which shop this event belongs to`

Here that equality is broken: `HMAC(raw_body)` is verified, but `request.shop` (used to build `WebhookMetadata` and dispatched to the app's handler) comes from a header that is never included in `to_signable_string`. This is a direct match for the "bytes verified vs. bytes parsed / field acted on but not covered by the HMAC" identity-binding break called out in scope.

### Impact Explanation
Any user who can install the target app on a shop they control can capture a legitimately Shopify-signed webhook (raw body + `hmac-sha256` header) delivered to their own tenant, then replay that exact same body/HMAC pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop. `HmacValidator.validate` still returns `true` because it only checks the untouched body against the untouched signature. `Registry.process` then dispatches the handler with `shop: request.shop` set to the victim's domain, so app-side logic that trusts `request.shop`/`WebhookMetadata#shop` for tenant scoping (e.g., updating tenant-specific records, invalidating/creating data keyed by shop) executes cross-tenant. This satisfies the Critical impact criterion "cross-tenant access."

### Likelihood Explanation
Exploitation requires only: (1) installing the app on an attacker-controlled shop (or dev store) to receive at least one webhook with a valid HMAC, and (2) the ability to send an arbitrary HTTP POST with modified headers to the app's public webhook endpoint — no access token, `client_secret`, or privileged Shopify account is required. This is achievable by any unprivileged internet user who can install a public app.

### Recommendation
Bind the tenant identity into the signed material, or otherwise cryptographically tie the `shop-domain` header to the verified payload, e.g., by including `shop`, `topic`, and `webhook_id` headers in the string that is HMAC-verified (mirroring what `AuthQuery#to_signable_string` does for OAuth), or by requiring the app layer to independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation before trusting it for tenant-scoped operations.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture one real webhook delivery, e.g. `orders/create`, noting `raw_body` (`B`), `X-Shopify-Hmac-Sha256: H`, and other headers.
2. Confirm `H == Base64(HMAC-SHA256(client_secret, B))` — i.e., `H` is computed purely from `B` per `Request#to_signable_string` / `HmacValidator#compute_signature`: [5](#0-4) 
3. Re-send an HTTP POST to the app's webhook endpoint with the identical body `B` and `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, `X-Shopify-Topic` unchanged.
4. `Registry.process` calls `HmacValidator.validate(request)`, which passes because `B` and `H` are unmodified.
5. The registered handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the payload actually originated from and describes the attacker's own shop, demonstrating cross-tenant identity confusion: [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
