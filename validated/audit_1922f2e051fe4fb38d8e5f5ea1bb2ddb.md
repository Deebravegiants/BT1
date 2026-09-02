### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted for tenant/event identity but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then forwards `request.shop`, `request.topic`, and `request.webhook_id` — all of which are read from unsigned HTTP headers — to the host application's handler as trusted identity fields. Because the HMAC only binds the *body* to the secret, not the headers, any party who can obtain one valid `(body, hmac)` pair can freely resubmit it with a different `shop-domain` (or `topic`/`webhook-id`) header and the signature check will still succeed.

### Finding Description
`HmacValidator.validate` computes/verifies the signature only over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns just the raw HTTP body — none of the Shopify headers are included: [2](#0-1) 

The `shop`, `topic`, and `webhook_id` accessors are all parsed straight from headers with no cryptographic binding to the body/HMAC: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body) and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` as the tenant/event identity passed into the application's webhook handler: [4](#0-3) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality the gem implicitly assumes is `hmac_signed_bytes == (shop, topic, webhook_id, body)`, but the code actually verifies only `hmac_signed_bytes == (body)`. `shop` is used by host apps (via `WebhookMetadata`) to select which tenant's data/session the webhook payload applies to, so forging it constitutes crossing a tenant boundary.

### Impact Explanation
Because the app's `api_secret_key` is shared across every shop that installs the app (it is not shop-specific), a legitimate merchant of Shop A (an unprivileged party who receives genuine webhook deliveries for their own shop) can capture one valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `shopify-shop-domain` header changed to Shop B, or with the `shopify-topic`/`shopify-webhook-id` headers altered. `Utils::HmacValidator.validate` still returns `true` (it never inspected those headers), so `Registry.process` will invoke the host application's handler with `WebhookMetadata` claiming the forged shop/topic/webhook-id. Any host application that uses `WebhookMetadata#shop` to look up sessions, write records, or gate per-tenant logic (the intended and documented use of this field) can be tricked into acting on/for the wrong tenant — a cross-tenant access issue.

### Likelihood Explanation
Exploitation only requires possession of one legitimately-received webhook payload for any shop that has the app installed (trivially obtainable by any merchant who installs the app themselves, or by intercepting the webhook once, since delivery is normal outbound HTTP from Shopify with no TLS pinning enforced by the gem) plus the ability to send an HTTP request with attacker-controlled headers to the app's public webhook endpoint. No `api_secret_key`, access token, or privileged account is required — this fits the "unprivileged internet user" threat model.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or independently verify that `request.shop` matches a shop that this app instance actually has an active session/webhook registration for before dispatching to handlers. At minimum, document that host applications must not use `WebhookMetadata#shop`/`#topic`/`#webhook_id` as trusted values without separate verification (e.g., cross-checking against `Registry`'s own registration state or a stored session for that shop).

### Proof of Concept
1. App has two merchants installed: `shop-a.myshopify.com` and `shop-b.myshopify.com`, sharing the same app `api_secret_key`.
2. Attacker (owner of `shop-a.myshopify.com`) receives a legitimate webhook: body `{"id":1,...}` with header `x-shopify-hmac-sha256: <valid hmac of body>` and `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate` in `hmac_validator.rb` recomputes the HMAC over the (unchanged) body and it matches — validation passes.
5. `Registry.process` (`registry.rb:188-200`) builds `WebhookMetadata.new(..., shop: "shop-b.myshopify.com", body: <shop-a's original payload>, ...)` and invokes the host handler, which now believes shop-a's data belongs to shop-b.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
