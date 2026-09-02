### Title
Webhook `shop` field is trusted by the handler but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator` only authenticates that string against the app's shared `client_secret`. The `shop` (and `topic`/`webhook_id`/`api_version`) header values are never included in the signed payload, yet `Registry.process` passes `request.shop` straight into `WebhookMetadata` and hands it to the app's handler as the authoritative tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `HmacValidator.validate` computes/compares the HMAC purely over that signable string: [2](#0-1) 

Meanwhile `shop` is read directly from an HTTP header with no cross-check against the signed body: [3](#0-2) 

`Registry.process` validates the HMAC of the body, then forwards `request.shop` (the unauthenticated header) into `WebhookMetadata`, which is the only tenant identifier passed to the app's handler: [4](#0-3) 

The documented equality the gem implies to the host app is: `hmac_valid(body) ⇒ shop_header is authentic for that body`. In reality the equality only holds for `hmac_valid(body) ⇒ body is authentic`; the `shop` header is never bound into the signature. Because all shops installed on a given app share the same `client_secret`, any body that was legitimately signed for shop A (e.g., a webhook payload the attacker received for their own store, which they fully control as an "unprivileged internet user" with a dev/test store) carries a signature that remains valid if replayed with the `shop` header rewritten to victim shop B. `Registry.process` will accept it (`HmacValidator.validate` passes because it only checks the body) and dispatch it to the handler as if it originated from shop B.

### Impact Explanation
This breaks the tenant binding `hmac_signed(body) == (body, shop)` down to `hmac_signed(body) == body`, letting an attacker who controls one shop's outbound webhook traffic to their own endpoint replay/re-route the resulting payload to the app's webhook endpoint under an arbitrary victim shop identifier. Downstream, most integrating apps (per the gem's own documented usage pattern in `docs/usage/webhooks.md`, which shows `data.shop` used directly for looking up sessions/queuing per-tenant jobs) will treat `data.shop` as trusted, enabling cross-tenant data confusion/access — the app processes attacker-supplied body content under the identity of a shop the attacker does not control.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus a subscription on any shop (even the attacker's own free/dev store) that receives the same topic, so the attacker can capture a validly-signed body/HMAC pair. No secret material, session, or privileged account is needed — this fits the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed material verified by `HmacValidator`, or independently authenticate the shop domain (e.g., cross-check it against a shop that has an active webhook registration/session before dispatch) rather than trusting the header verbatim once only the body has been proven authentic.

### Proof of Concept
1. Attacker registers the app on their own shop `attacker.myshopify.com` and subscribes to a webhook topic (e.g., `orders/create`).
2. Shopify sends a webhook to the attacker's own endpoint with a body `B` and header `shopify-hmac-sha256: HMAC(secret, B)` plus `shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same body `B` and HMAC header to the target app's public webhook endpoint, but sets `shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — this still matches because `B` and the HMAC are unmodified. [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-originated body, processed as if it were a genuine webhook from the victim shop. [6](#0-5)

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
