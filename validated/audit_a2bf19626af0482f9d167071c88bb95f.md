### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC only over the raw request body, while the `shop` (tenant identifier) is read from an HTTP header that is never included in the signed data. Any party that can obtain one validly-signed webhook payload for their own shop (e.g., by installing the app themselves) can replay that same body/HMAC pair while substituting the `x-shopify-shop-domain` header for a victim shop, and the app will accept and process it as if it originated from the victim tenant. This mirrors the Curve report's bug class: a field that is acted upon (`get_dy`'s `i`/`j`/`dx` parameters vs. the interface actually verified) is not the field actually covered by the check — here, the `shop` field consumed by webhook handlers is not the field covered by the HMAC.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived purely from an unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which only checks `to_signable_string` (the body) against the HMAC — and then forwards `request.shop` straight into `WebhookMetadata`, which is handed to the app's registered handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms the check is scoped strictly to `to_signable_string`, never to headers: [4](#0-3) 

`WebhookMetadata.shop` is a plain, unauthenticated string field consumed by the handler as the tenant identifier: [5](#0-4) 

The identity binding that should hold is: `shop asserted to handler == shop cryptographically bound by HMAC`. In this implementation that equality does not hold — the HMAC binds only the JSON body bytes; the `shop` header is orthogonal and unauthenticated. Because the HMAC secret (`api_secret_key`) is shared across all shops installing the same app, any legitimately-installed merchant (an "unprivileged" party with respect to other tenants of the same app) can capture a real, validly-signed webhook delivered for their own shop and resubmit it to the app's webhook endpoint with the `shop-domain` header swapped to another shop's domain. The body and its HMAC remain valid because they are untouched; only the header — which is never checked — differs.

### Impact Explanation
This breaks the tenant boundary the library is expected to enforce: the app's webhook handler will process a request under an attacker-chosen victim shop identity while the actual signed content is unrelated to that shop. Depending on the topic replayed (e.g. `app/uninstalled`, `shop/redact`, `customers/redact`, `orders/create`), this can drive cross-tenant state corruption in the hosting application: deleting/deactivating a different merchant's session or data, triggering GDPR redaction flows for the wrong shop, or injecting fabricated business data attributed to a shop that never sent it. This qualifies as cross-tenant access, matching the Critical impact category in scope.

### Likelihood Explanation
Exploitation requires no knowledge of `api_secret_key`, access tokens, or any credential belonging to the victim shop. The attacker only needs to be a legitimate installer of the app on their own store (a normal, low-privilege position any internet user can reach by installing a public app) to obtain one valid signed webhook body/HMAC pair, then simply resend it to the app's public webhook endpoint with a different `shop-domain` header value. This is a mechanical, low-effort replay requiring only observation of the app's own webhook traffic.

### Recommendation
Bind the shop identity into the verified signable data, or otherwise cryptographically tie the `shop-domain` header to the signed payload before trusting it. Concretely, `Request#to_signable_string` (or `HmacValidator`) should incorporate the `shop-domain` (and ideally `topic`/`webhook-id`) headers into what is verified, or the registry should independently confirm that the `shop` header corresponds to a shop session/subscription the app actually expects for that specific webhook delivery, rejecting mismatches instead of trusting the header value verbatim.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic to receive a legitimate delivery with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`.
2. Capture the raw request (`B`, headers including `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: H`).
3. Resend the exact same body `B` and HMAC header `H` to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `B` only [4](#0-3)  — validation succeeds because `B` and `H` are unchanged.
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` [6](#0-5)  and processes attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
