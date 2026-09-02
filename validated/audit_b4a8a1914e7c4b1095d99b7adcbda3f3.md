### Title
Webhook Shop/Topic/API-Version Identity Not Bound by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers that are never included in the signed content. This breaks the identity binding `shop authenticated == shop acted upon`, mirroring the reported bug class where a value used downstream (`curTakerFillAmount`/here, the tenant identity) is not actually covered by the verification that is assumed to protect it.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC solely against that signable string (the body): [2](#0-1) 

`Registry.process` gates on this body-only HMAC check and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all of which are read straight from HTTP headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) that are not part of the signed payload: [3](#0-2) [4](#0-3) 

The equality the gem implicitly assumes is:
`shop bound by HMAC == shop delivered to handler.handle(...)`

In reality:
`shop bound by HMAC (raw body bytes only)` ≠ `shop read from unauthenticated header and passed to WebhookMetadata`

Any party that can obtain one validly-signed webhook body+HMAC pair for their *own* shop (a normal, legitimate webhook delivery any merchant with the app installed receives) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `topic`/`webhook-id`/`api-version`) header for a different, victim shop. `HmacValidator.validate` still passes because it only checks the raw body against the secret; `Registry.process` then dispatches `handler.handle` with `WebhookMetadata.new(shop: <attacker-chosen>, body: <original>, ...)`. The host application's handler — following this gem's documented contract that a passing HMAC check means the delivered `WebhookMetadata` is authentic for that `shop` — will process/store the payload under the wrong tenant.

### Impact Explanation
This crosses a tenant boundary: an unprivileged actor who is themselves a legitimate merchant (no access token, no `client_secret`, no privileged account needed) can cause the app to associate one shop's webhook data with another shop's identity, i.e., cross-tenant data injection/confusion. This matches the Critical "cross-tenant access" impact category, since it defeats the tenant-isolation guarantee that the HMAC check is supposed to provide for webhook `shop` identity, purely through the gem's own `Registry.process`/`Request` logic (not by the host app ignoring the API).

### Likelihood Explanation
Requires only: (1) being a merchant who legitimately receives at least one real webhook from Shopify for their own shop (trivial to obtain — install any app, trigger any webhook topic), and (2) sending a crafted HTTP request to the target app's public webhook endpoint with the captured body/HMAC and a modified `shop-domain` header. No secrets, tokens, or elevated access are required, making this practically exploitable by any internet user with a Shopify Partner/dev store account.

### Recommendation
Bind the tenant/topic identity into the authenticated content instead of trusting bare headers:
- Include `shop`, `topic`, and `api_version` in the value that is HMAC-verified (e.g., verify against a canonical string built from headers + body, or require the host app to independently confirm `shop` against its own session/install records before trusting `WebhookMetadata.shop`).
- At minimum, document prominently that `WebhookMetadata.shop`/`topic`/`webhook_id` are NOT cryptographically bound to the HMAC-validated body, and that host apps must correlate the shop against their own installed-shop/session store before acting on webhook data.
- Consider validating that the resolved shop is one that currently has an active session in the app's session storage before dispatching to a handler.

### Proof of Concept
1. Attacker installs the target app on their own dev shop `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` that Shopify computed over `B` with the app's `client_secret`.
2. Attacker sends a POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid because it only signs `B`)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
3. `Webhooks::Request.new` parses these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` (`= B`) and matches `H` — validation succeeds.
4. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...))`, causing the host app to process/store attacker-controlled order data as if it belongs to `victim-shop.myshopify.com`. [3](#0-2) [5](#0-4)

### Citations

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
