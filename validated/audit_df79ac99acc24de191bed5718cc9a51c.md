### Title
Webhook `shop-domain` header not covered by HMAC allows cross-tenant webhook shop-spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable material solely from the raw JSON body [1](#0-0) , while the `shop` (and `topic`) values used downstream to identify the tenant are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` verifies only the HMAC over the body via `Utils::HmacValidator.validate(request)` and, on success, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler [3](#0-2) . Because the shop-domain header is never part of the HMAC-signed material, any request bearing a *valid* body+HMAC pair is accepted regardless of which shop's domain is asserted in the header.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field [4](#0-3) . For webhooks, `to_signable_string` returns only `@raw_body` [1](#0-0) ; the `shop` accessor is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed payload at all [5](#0-4) .

The equality the gem should enforce is:
`shop_bound_by_hmac == shop_used_for_tenant_identification`

but what it actually enforces is:
`HMAC(secret, body) == received_hmac` AND `shop_used_for_tenant_identification == header_value` (unauthenticated)

These are not the same binding. Since the webhook endpoint is a public HTTP endpoint reachable by any internet client (that is the entire point of webhook delivery), an attacker who has legitimately received one webhook for their own shop (e.g., by installing the app on a shop they control, or simply from any topic where they can trigger a webhook to themselves) obtains a valid `(raw_body, hmac)` pair signed with the app's real secret. They can then replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `Registry.process` still finds the HMAC valid (it never depended on the header) and dispatches to the handler with `WebhookMetadata#shop` set to the attacker-chosen value [6](#0-5) .

Any host application that uses `data.shop` from `WebhookMetadata` to look up the correct merchant session/access token to act on the webhook (which is the documented usage pattern, since sessions are keyed by shop) will now perform that action against a shop the attacker does not control, using attacker-controlled body content that was never actually sent by Shopify for that shop.

### Impact Explanation
This breaks the tenant binding between "the shop whose secret validated the payload" and "the shop the payload is attributed to and acted upon," which is exactly the class of identity-binding failure in scope (an authenticated/verified value acted upon vs. an unauthenticated field used for identification). Impact is cross-tenant confusion: an attacker can inject fabricated webhook events attributed to any victim shop known to be installed on the app, causing the host application to process attacker-controlled data (e.g., fake `orders/create`, `app/uninstalled`, GDPR topics) under the victim's identity/session. Depending on the handler's logic this can range from data corruption to triggering privileged actions (e.g., uninstall cleanup, redaction flows) against the wrong tenant.

### Likelihood Explanation
Moderate-to-high for apps installed on many shops / dev stores: any shop that can install the app (including a free/dev store the attacker controls) can harvest a valid `(body, hmac)` pair for a chosen topic, then replay it against the same public endpoint with a forged `shop-domain` header naming any other installed shop. No secret, token, or privileged access is required beyond having the app installed on one attacker-controlled store — a normal, unprivileged action.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise cryptographically/independently verify that the header-asserted shop matches a shop actually entitled to send that specific signed payload (e.g., require the caller to supply the expected shop and compare it against a value that is provably tied to the signed body, rather than trusting the `shop-domain` header verbatim in `Webhooks::Request#shop`). At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are NOT covered by the HMAC and must not be used by host applications to select which merchant session to act upon without additional verification.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the raw POST body and the genuine `x-shopify-hmac-sha256` value Shopify sends.
2. Send a new HTTP POST to the app's webhook endpoint with:
   - The exact same raw body and `x-shopify-hmac-sha256` captured in step 1.
   - `x-shopify-shop-domain: victim.myshopify.com` (any shop the attacker knows has the app installed).
   - `x-shopify-topic` set to the same topic used in step 1.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) , which succeeds because the HMAC only ever covered the body, unchanged from step 1.
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker body>, ...)` [6](#0-5) , causing the host application to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-23)
```ruby
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
