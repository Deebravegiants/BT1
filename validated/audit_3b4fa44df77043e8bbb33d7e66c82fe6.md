### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw request body only, while `shop` (and `topic`) are read directly from HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) , and `Utils::HmacValidator.validate` computes the HMAC over that signable string and compares it against the `hmac` field taken from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header [2](#0-1) . However, `Request#shop` is derived from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of `to_signable_string` at all [3](#0-2) . `Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` to build the tenant-identifying `WebhookMetadata` passed to the app's handler [4](#0-3) .

This breaks the equality that should hold: `shop authenticated by HMAC == shop used to identify the tenant`. Because the header is unauthenticated, a party who has captured one valid `(raw_body, hmac)` pair for a webhook topic (e.g., from a webhook delivered to a shop they control, or a body whose payload does not itself uniquely bind to a shop) can resubmit that exact body/HMAC pair with an arbitrary `shopify-shop-domain` header value. The signature check in `Registry.process` will still pass, since it only verifies `raw_body` against `hmac`, and the handler will be invoked believing the event originated from the attacker-chosen shop.

### Impact Explanation
This meets the High-severity bar ("cross-tenant access") from the analog criteria: an app relying on `WebhookMetadata#shop` from this gem to select a tenant's session/data (a common integration pattern in Shopify apps) can be made to process or persist forged data under a victim shop's identity, without needing the app's `api_secret_key` or any privileged credential — only a previously-observed valid webhook body/HMAC pair (which is retrievable by anyone who has an app installed, since Shopify webhooks aren't stored secretly by the receiving endpoint).

### Likelihood Explanation
Moderate: the attacker must possess at least one legitimately-signed `(body, hmac)` pair (obtainable by installing the app to their own store and capturing a webhook delivery, which any developer/merchant can do), and the target handler logic must not itself validate shop-derived identifiers embedded in the JSON payload (many topics' payloads don't include a shop domain field, relying instead on the header). This is a structural gap in the gem, not merely a misuse by the app.

### Recommendation
Either (a) require the app to independently verify `request.shop` against an app-controlled trusted store/allowlist before acting on `WebhookMetadata`, and clearly document that `shop` is unauthenticated, or (b) change `Request#to_signable_string` / `HmacValidator` usage for webhooks to bind the `shop-domain` (and `topic`) header values into the material that is validated, so that any mismatch between the header and what Shopify actually signed is detected. At minimum, the library should not silently pass an unauthenticated `shop` value through to handler code without a clear warning in `docs/usage/webhooks.md`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with raw body `B` and header `x-shopify-hmac-sha256: H` (a valid HMAC of `B` under the app's secret) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com` (and, if desired, `x-shopify-webhook-id` to avoid dedup checks).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`, unchanged) and compares to `H` — validation succeeds [5](#0-4) .
4. `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` [6](#0-5)  — the app processes attacker-controlled data under the victim shop's tenant context, even though the shop value was never covered by the cryptographic signature.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
