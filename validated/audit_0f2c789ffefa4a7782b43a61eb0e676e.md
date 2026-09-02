### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw request body only, while the `shop` (tenant identifier) is read from an HTTP header that is never included in the signed bytes. This breaks the identity binding `shop authenticated == shop acted upon`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC only over `to_signable_string` (the raw body), never over the shop header: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` (the unauthenticated header) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the app's `client_secret`/webhook secret is shared across all shops that install the app (it is not per-shop), any attacker who can legitimately install the app on their own store (or otherwise obtain one valid `(raw_body, hmac)` pair from Shopify) can compute a valid signature for arbitrary body content signed with the same shared secret. Since the `shop-domain` header is excluded from `to_signable_string`, the attacker can replay that same raw body and valid HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` because the body/HMAC pair is genuinely valid, but the `shop` value delivered to the handler is attacker-controlled and disconnected from the entity that actually produced the signed body.

This is exactly the identity-binding break called out in scope: "a field acted on but not covered by the HMAC." The equality that should hold is `shop-that-produced-hmac == shop-passed-to-handler`, but the gem never establishes it — the HMAC binds only the body bytes to the shared secret, not the tenant identity.

### Impact Explanation
This enables cross-tenant confusion in webhook processing: an attacker-controlled `shop` value can be delivered to the host application's webhook handler alongside a cryptographically valid HMAC, even though that shop never actually sent the associated payload. Any app logic that trusts `WebhookMetadata#shop` as an authenticated tenant identifier (e.g., to select which merchant's data record to update, or to authorize a mandatory GDPR/compliance webhook such as `customers/redact` or `shop/redact` for a shop the attacker does not control) can be tricked into acting on/for a shop the attacker does not own. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Medium: exploitation requires the attacker to have at least one legitimately-signed `(raw_body, hmac)` pair — trivially available to anyone who installs the app on their own (attacker-controlled) development store, since Shopify will deliver correctly signed webhooks to that installation using the same app-wide secret. The attacker then only needs to replay the body with a modified `shop-domain` header to the app's public webhook endpoint, which requires no access to `api_secret_key`, access tokens, or any privileged account beyond a self-service store installation.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the same authenticated bytes that the HMAC covers, e.g., by cryptographically tying the header value into the signable string, or by requiring host applications to cross-check `request.shop` against a shop already known/authorized for that specific `webhook_id`/subscription rather than trusting the header outright. At minimum, document clearly that `Webhooks::Request#shop` is not itself authenticated by the HMAC and must not be treated as a trusted tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, receiving a legitimate webhook: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`, verified via `HmacValidator.validate`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
2. Attacker resends body `B` with the same `x-shopify-hmac-sha256: H` header, but sets `x-shopify-shop-domain: victim.myshopify.com` in the POST to the app's webhook endpoint.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` (`lib/shopify_api/webhooks/registry.rb:188-190`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `request.shop` returns `"victim.myshopify.com"` from the (unauthenticated) header (`lib/shopify_api/webhooks/request.rb:20-23`), which is passed into `WebhookMetadata` and handed to the app's registered handler as if the victim shop generated the event (`lib/shopify_api/webhooks/registry.rb:198-199`).

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
