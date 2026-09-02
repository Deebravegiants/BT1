### Title
Webhook tenant identity (`shop`) is asserted from an unauthenticated header while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats the `X-Shopify-Shop-Domain` header as the authoritative tenant identifier after passing HMAC validation, but the HMAC only covers the raw request body, not the `shop-domain` header.

### Finding Description
`Utils::HmacValidator.validate` is called on the `Request` object, which computes/compares the signature only against `to_signable_string`, defined as the raw body: [1](#0-0) 

The `shop` accessor used downstream, however, is read straight from the `shopify-shop-domain` (or `x-shopify-shop-domain`) HTTP header, which is not part of the signed material at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (from the unauthenticated header) to build the `WebhookMetadata` passed to the host app's handler, which is the value the host app uses to identify which merchant/tenant the webhook belongs to: [3](#0-2) 

This is the same bug class as the M-25 report: a value that is *used* to make a security-relevant decision (tenant identity here, vs. `balanceBefore`/`balanceAfter` there) is not actually bound by the verification step that is supposed to authenticate it. The identity binding that should hold is: `hmac_verified_sender == shop_asserted_in_metadata`. Because only the body bytes are covered by the signature, an attacker who can produce a body/signature pair valid for their own `shop`, and then re-send it with a modified `shop-domain` header pointing at a victim shop, would break this binding — the gem would deliver an event with a HMAC that "validated" but a `shop` claim that was never authenticated.

### Impact Explanation
If exploitable, this allows cross-tenant confusion: a webhook payload correctly signed for shop A could be relayed with the `shop-domain` header rewritten to shop B, causing host applications (which rely on `WebhookMetadata#shop` as validated/trusted, per this gem's documented contract) to attribute merchant A's data/event to merchant B, or to act on merchant B's tenant context using merchant A's payload. This matches the "cross-tenant access" impact bucket.

### Likelihood Explanation
Exploitation requires an attacker to control or intercept a legitimately-HMAC'd webhook body for *some* shop (their own dev/test shop is sufficient, since HMAC is computed over the secret + body only, independent of shop) and to be able to re-deliver it to the app's webhook endpoint with an altered `shop-domain` header — the endpoint itself is normally reachable over the public internet since it's designed to receive Shopify webhooks. This does not require any credentials, access tokens, or the app's `client_secret`.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values into the signed material, or otherwise cryptographically tie them to the verified body (e.g., by including them in `to_signable_string`, or documenting/enforcing that host apps must independently re-validate the shop against a known registration before trusting `WebhookMetadata#shop`). At minimum, the library should not label a request as "validated" via `HmacValidator.validate` while still exposing unauthenticated header-derived fields as if they were verified.

### Proof of Concept
1. Obtain a valid `(raw_body, hmac-sha256)` pair for a webhook delivered to shop `attacker.myshopify.com` (e.g., by installing the app on a shop you control and capturing a real webhook delivery).
2. Replay the same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds (it only checks `raw_body` against the secret) as shown in [4](#0-3) .
4. `Registry.process` proceeds to call `handler.handle` with `WebhookMetadata.new(... shop: request.shop ...)` set to `victim.myshopify.com`, even though the payload was never signed in association with that shop, as shown in [3](#0-2) .

**Note on uncertainty:** I could not verify from this index how, or whether, downstream host applications (or Shopify's own webhook delivery infrastructure/transport, e.g. mutual TLS or source IP allow‑listing) provide additional out-of-band assurance about the `shop-domain` header outside of what this gem does. This gem's own code path does not bind `shop` to the HMAC, but full exploitability depends on transport-level protections outside this gem's scope, which I cannot confirm from the indexed files.

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
