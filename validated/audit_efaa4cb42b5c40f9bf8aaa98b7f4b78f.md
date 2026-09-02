I found a concrete analog matching the report's bug class ("a field acted on but not covered by the HMAC").

### Title
Webhook shop-domain header is trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The `_harvestCore()` report cites a value (`roi`) being computed from data (`loss`) that is derived from state the function had already accounted for elsewhere, producing an internal inconsistency between what is verified/computed and what is acted upon. The structural analog here is a value that the code *acts on* (routes/attributes to a tenant) without that value being *bound by the same integrity check* that gates trust in the request.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` verifies the HMAC strictly against that signable string [2](#0-1) . The `shop` value, however, is read directly from the `x-shopify-shop-domain` header, which is never included in the signed bytes [3](#0-2) . `Registry.process` validates the HMAC and then immediately uses `request.shop` to build `WebhookMetadata` passed to the app's handler [4](#0-3) .

The binding that should hold is: `hmac_verified_bytes ⊇ {shop}`. In reality: `hmac_verified_bytes = raw_body` only, while `shop = header["x-shopify-shop-domain"]`, i.e. `shop ∉ hmac_verified_bytes`. Genuine Shopify webhook deliveries do set this header consistently with the signed body, but the gem's own validation logic does not enforce that consistency — it only proves the body wasn't tampered with, not which shop it came from.

### Impact Explanation
Given a webhook HTTP handler in a host application that (as this gem documents and expects) calls `Registry.process(request)` and trusts `request.shop` for tenant attribution (e.g., looking up which merchant record to update, scoping data mutations, GDPR redaction target, etc.), an attacker who can influence or replay the `x-shopify-shop-domain` header on an otherwise validly-HMAC'd request (e.g. a request with a body previously observed for shop A, replayed/relayed with the header rewritten to shop B) would have that request accepted as valid and attributed to the wrong tenant, because `HmacValidator.validate` never checks the header. This is a cross-tenant data integrity issue: `process` treats `(valid_hmac_of_body) ⇒ (trust_shop_header)`, which is not a sound implication.

### Likelihood Explanation
Exploitation depends entirely on whether the transport delivering webhooks to the host application allows the `x-shopify-shop-domain` header to be modified independently of the signed body (e.g., an intermediary proxy, a replay across environments sharing one `client_secret`/webhook secret, or any host setup that does not treat the header as immutable/tied to a specific inbound connection from Shopify's known IP ranges). This is a real gap in the library's own verification code — the gem is solely responsible for `HmacValidator.validate` and `Request#shop`, and it does not fail-closed if the header and body's shop diverge; it does not depend on the host app misusing an undocumented API, since `shop` is the library's own documented accessor for webhook shop attribution.

### Recommendation
Extend `Webhooks::Request#to_signable_string` (or add a companion check in `Registry.process`) to bind `shop-domain` (and ideally `topic`, `webhook-id`) into the value verified by the HMAC, or otherwise cryptographically tie the header to the signed body before it is used for tenant routing, so that `HmacValidator.validate(request)` can only return true when `shop` is provably the same value Shopify signed for that body.

### Proof of Concept
1. Capture a legitimate webhook delivery for `shop-a.myshopify.com` with body `B` and valid `hmac = HMAC(secret, B)`.
2. Replay the same request to the app's webhook endpoint, keeping `raw_body = B` and the valid `hmac` header unchanged, but set `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(secret, B) == hmac` [5](#0-4) .
4. `Registry.process` proceeds and calls the handler with `shop: "shop-b.myshopify.com"` [6](#0-5) , causing the host app to attribute shop-a's webhook payload to shop-b.

**Note on confidence**: I was not able to fully verify, within the available index, whether any host-application-facing documentation (`docs/**`, excluded from scope) explicitly warns developers to independently re-validate `shop-domain` against connection-level metadata (e.g., IP allowlisting) before trusting `request.shop`; if such guidance exists and is followed, it would mitigate but not eliminate the gap in the library's own verification primitive.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
