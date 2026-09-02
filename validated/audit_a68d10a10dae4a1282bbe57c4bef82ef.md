### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw HTTP body against the HMAC signature. The `shop`, `topic`, `webhook_id`, and `api_version` values — which come from separate, unsigned HTTP headers — are handed to the app's handler untouched. Any party that can obtain one genuine webhook delivery (e.g. an attacker who installs the app on their own store) can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop, and the gem will accept it as authentic and attribute it to the victim tenant.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string` only: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw request body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers that are never mixed into the signable string: [3](#0-2) 

`Registry.process` performs exactly one check — HMAC of the body — and then builds `WebhookMetadata` (which is passed to the app's handler) directly from these unauthenticated headers, including `shop`: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified(body) == authenticated(shop, topic, webhook_id)`. In reality the equality only holds for `HMAC-verified(body) == authenticated(body)`; `shop` (and the other headers) are asserted, not verified. This is the same bug class as the `Goldilend.repay()` report — the check validates one quantity (`body`/`interest`) but the code acts on a different, unverified quantity (`shop` header/`userLoan.interest`) as if it had been covered by the same guarantee.

### Impact Explanation
Any entity able to install the app on a store they control (an "unprivileged internet user" with respect to other merchants' data) receives genuine webhook deliveries from Shopify with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared secret. Because the shop-domain header is outside the signed scope, that same body + HMAC pair can be replayed to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to any victim shop. `Registry.process` will accept it (HMAC still matches the unchanged body) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that keys webhook processing by `data.shop` (the officially documented field for this purpose) will apply attacker-controlled webhook data to another tenant's account — a cross-tenant access/data-integrity violation.

### Likelihood Explanation
Exploitation requires no secrets, no privileged account, and no interception of other tenants' traffic: the attacker only needs to install the target app on their own store (a normal, unprivileged action), capture one of their own legitimate webhook deliveries, and resend it to the public webhook endpoint with a forged `shop` header. The webhook endpoint is, by design, an unauthenticated public HTTP endpoint reachable by any internet client. Likelihood is therefore high for any app relying on the documented `shop`/`topic` header trust model.

### Recommendation
Bind the identity fields to the signature instead of trusting bare headers:
- Either include `shop`, `topic`, and `webhook_id` in the signable string that is HMAC-verified, or
- Independently verify `request.shop` against a value already associated with the specific webhook subscription/session (e.g. looking up the expected shop for the `webhook_id`) before invoking the handler, rejecting mismatches.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` (legitimate self-registration).
2. Attacker triggers an event (e.g., creates an order) causing Shopify to deliver a real webhook: body `B`, headers `X-Shopify-Hmac-Sha256: H = HMAC_SHA256(secret, B)`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker captures `B` and `H` from their own inbound traffic (no interception of anyone else's traffic needed).
4. Attacker POSTs body `B` with header `H` unchanged to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Registry.process` calls `HmacValidator.validate`, which recomputes `HMAC_SHA256(secret, B)` — still equal to `H` — and passes.
6. `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...))` executes, causing the app to process attacker-supplied content as if it originated from `victim.myshopify.com`. [5](#0-4) [6](#0-5)

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
