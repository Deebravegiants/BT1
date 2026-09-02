Confirmed root cause. The `shop-domain` header is read directly from the request and handed to the handler without any cryptographic binding to the HMAC, which is computed only over the raw body. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Registry.process` validates covers **only** `raw_body`. The `shop-domain` header — which `Registry.process` passes straight to the app's handler as the tenant identifier — is never part of the signed bytes. An attacker who can obtain any single valid `(body, hmac)` pair for the app (e.g. by installing/using the app on a store they control, or intercepting one webhook delivery) can replay that exact body/hmac while substituting an arbitrary `x-shopify-shop-domain` header value, and `Utils::HmacValidator.validate` will still return true.

### Finding Description
`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns `@raw_body` only — headers, including `shop`, `topic`, `webhook_id`, and `api_version`, are excluded from the signable string. The equality the gem should enforce is: `shop header used by the handler == shop that the secret-holder (Shopify) attested for this exact payload`. Because only the body is signed, this equality is not enforced — the same valid `(body, hmac)` pair can be paired with any `shop-domain` header value and still pass validation.

An unprivileged attacker with an app install on any store (even a free/trial store) can capture one legitimate webhook delivery for that store, then resend the identical body and HMAC to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. Since `Context.api_secret_key` is a single shared secret for the whole app (not per-shop), the HMAC validates successfully, and `WebhookMetadata.shop` — trusted by the host app to select per-tenant session/data — will contain the attacker-chosen value instead of the value actually attested to that payload.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: the `shop` field handed to app code is unauthenticated data attacker can freely set for a resend of a captured, otherwise-valid payload. Depending on how the host app uses `data.shop` (e.g., looking up a stored access token/session for that shop, writing data associated with that shop, or triggering compliance actions such as `customers/redact` for an arbitrary shop), this enables cross-tenant data confusion/injection under a shop identity the attacker does not control. This matches the "cross-tenant access" impact class since the shop binding meant to scope the webhook to one merchant is not cryptographically enforced.

### Likelihood Explanation
Exploitability requires the attacker to first obtain one legitimate `(body, hmac)` pair, which is achievable simply by installing the target app on any shop they control (or any shop where they can observe outgoing webhook traffic) — no leaked secrets or privileged access are needed. The webhook endpoint is intentionally public-facing per the gem's documented pattern.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook_id`) header values as part of the signable string used to compute the webhook HMAC, or otherwise cryptographically bind the shop claim to the payload before it is handed to the handler, e.g. by verifying the received `shop` against a shop the app expects for a given webhook_id/registration.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it register a webhook (e.g. `orders/create`).
2. Attacker triggers the event, and the app's endpoint receives:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker.myshopify.com
   body: {...}
   ```
3. Attacker resends the exact same raw body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `hmac_validator.rb` recomputes the HMAC over `raw_body` only, matches the attacker's unchanged hmac, and returns `true`.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", ...))`, and the host app's webhook handler processes/attributes attacker-supplied payload data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
