### Title
Webhook HMAC only covers the raw body, not the `shop`, `topic`, or `webhook_id` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, but its `to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers and are never included in the HMAC computation. `Registry.process` verifies only the body signature and then unconditionally trusts the header-derived `shop` value to build `WebhookMetadata` passed to the app's handler, breaking the binding `authenticated(bytes) == trusted(shop)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from request headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`HmacValidator.validate` (shared by webhooks and OAuth) computes `HMAC(secret, to_signable_string)` and compares it to the received `hmac`: [3](#0-2) 

`Registry.process` checks only this body-bound HMAC, then immediately trusts the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` to construct the metadata delivered to the app's business logic: [4](#0-3) 

Since the app's `api_secret_key` is a single shared secret across every shop that installs the app (this is the standard Shopify public-app credential model, not a per-shop secret), any party who can obtain one valid `(raw_body, hmac)` pair — e.g., by installing the app on their own free/dev store and capturing a webhook delivery for a topic they control — holds a signature that is cryptographically valid under the same secret for *any* shop. Because `shop`/`topic`/`webhook_id` sit outside the signed message, that attacker can replay the exact same `raw_body` + `hmac` pair directly against the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header for a victim shop's domain. `HmacValidator.validate` still succeeds because it only re-derives the HMAC over the identical body, and `Registry.process` hands the handler a `WebhookMetadata` claiming the forged victim `shop`, causing the host application to process/attribute attacker-controlled webhook data as if it originated from the victim tenant.

This is the same failure class as the audit report: an authenticated field (recovery request in the report; webhook body here) is accepted without binding the operative identity/state field (`account_id`+state there; `shop` here) into what's actually verified.

### Impact Explanation
This breaks the tenant identity boundary the gem is supposed to enforce for webhook processing: `verified(raw_body) == trusted(shop)` is false, since `shop` is never part of `verified()`. Any host application that dispatches business logic (e.g., updating orders, inventory, customer data, triggering integrations) keyed off `WebhookMetadata#shop` is exposed to cross-tenant data confusion/injection from an attacker who only needs low-privileged access to any single shop where the same app is installed (trivially obtainable via a free development store). This satisfies the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any multi-tenant public app: installing the app on an attacker-owned dev store to harvest a `(body, hmac)` pair requires no special privilege, and forging the `X-Shopify-Shop-Domain` header on a direct POST to the app's public webhook endpoint requires no credentials at all — it only requires the endpoint to be internet-reachable, which is the normal deployment model for Shopify app webhook receivers using this gem.

### Recommendation
Bind the identity fields into the verified message instead of trusting bare headers post-verification. At minimum, `Request#to_signable_string` should incorporate `shop`, `topic`, and `webhook_id`, or `Registry.process` should independently confirm that the header-derived `shop` corresponds to a shop that legitimately owns the specific `webhook_id`/subscription (e.g., by cross-checking against records created during registration) before dispatching to handlers. This mirrors the audit's fix of binding the recovery request to state via `cnt_rec`/`cnt_acc` rather than trusting an unbound, replayable signed payload.

### Proof of Concept
1. Attacker installs the target public app on their own (attacker-controlled) development shop, `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app for a topic the attacker controls, with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` — attacker captures both.
3. Attacker sends a direct POST to the app's public webhook endpoint with the exact same body `B` and HMAC header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and, if desired, a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `HmacValidator.validate` in [3](#0-2)  passes because it only checks `B` against `secret`.
5. `Registry.process` in [4](#0-3)  dispatches `WebhookMetadata` with `shop: "victim.myshopify.com"` to the handler, which processes attacker-supplied data as if it came from the victim shop.

### Citations

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
