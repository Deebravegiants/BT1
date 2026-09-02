## Title
Webhook shop identity used by handlers is taken from an unauthenticated header, not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` value that is handed to application webhook handlers is read from the `X-Shopify-Shop-Domain` HTTP header, a value that is never part of the signed data.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) , and `HmacValidator.validate` computes the HMAC strictly over that signable string against the `hmac` value pulled from the `hmac-sha256` header [2](#0-1) . The `shop` accessor, however, is derived independently from the `shop-domain` header and is not fed into `to_signable_string` at all [3](#0-2) . `Registry#process` validates only the HMAC of the request and then forwards `request.shop` (the unauthenticated header value) straight into `WebhookMetadata`, which is passed to the app's `WebhookHandler#handle` implementation as the tenant identity for the event [4](#0-3) .

The identity binding that should hold is: `shop` acted upon by the handler == `shop` cryptographically bound to the payload via HMAC. Before the fix/exploit: the HMAC binds only `raw_body` bytes to the secret; `shop` is out-of-band. After an attacker's request: the attacker takes a legitimate captured webhook body/HMAC pair (e.g., from their own store, or one seen on a public endpoint/log) and re-sends it with a different `X-Shopify-Shop-Domain` header value. `HmacValidator.validate` still succeeds because the header is not part of the signed string, but `Registry#process` now hands the handler a `WebhookMetadata` claiming a different, attacker-chosen `shop`, breaking the equality `authenticated_shop == shop_used_by_handler`.

### Impact Explanation
Any application built on this gem that trusts `WebhookMetadata#shop` to select tenant-scoped state (session lookup, data isolation, per-shop side effects) can be made to process a valid, HMAC-passing webhook under an attacker-chosen shop identity. This is a cross-tenant identity-binding break: the byte range that is cryptographically verified (body) is disjoint from the byte range that is semantically trusted and acted upon (header), classically enabling cross-tenant confusion once a webhook body/signature pair is obtained for replay.

### Likelihood Explanation
Exploitation requires the attacker to first obtain one valid `(raw_body, hmac)` pair — most straightforwardly one that Shopify sent for the attacker's own installed shop, or one leaked through logs/an exposed endpoint — and a network path to the app's webhook endpoint that does not additionally re-derive/validate the shop domain against, e.g., an active installation for that header value. Because `api_secret_key` is never required (only the pre-existing valid signature is reused, header is swapped), the barrier is moderate rather than high; the gem itself provides no mechanism to reject the mismatch.

### Recommendation
Include the `shop-domain` header (and ideally `topic`, `webhook-id`, and `api-version`) in the signable string used for HMAC verification, or, failing that, have `Registry#process` cross-check `request.shop` against the shop stored for a previously verified installation/session before dispatching to handlers. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be re-validated by the host application against its own session store before being trusted as a tenant key.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives (or otherwise observes) a legitimate webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker resends the exact same body `B` and header `H` to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes `HMAC-SHA256(secret, B)` (per `to_signable_string` returning only `@raw_body`) and it matches `H`, so validation succeeds [1](#0-0) [2](#0-1) .
4. `Registry#process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` from the spoofed header and dispatches it to the registered handler as if Shopify itself reported this event for `victim.myshopify.com` [4](#0-3) .

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
