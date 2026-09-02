### Title
Webhook shop attribution not bound to HMAC signature enables cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over the raw request body only. The `shop` identity that is handed to the app's webhook handler comes from an unsigned HTTP header (`x-shopify-shop-domain`), so the binding "authenticated shop == shop the handler acts on" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed body [2](#0-1) . `Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against a signature computed from `to_signable_string` (i.e., the raw body) [3](#0-2) . `Registry.process` trusts this validation and then forwards `request.shop` (the unauthenticated header) directly to the app's handler as the tenant identifier: [4](#0-3) .

Because a Shopify app's `client_secret` (used as the HMAC key) is the same for every shop that installs that app, any unprivileged user can install the app on their own (free/dev) store, receive a legitimately-signed webhook, and capture a valid `(raw_body, hmac)` pair. That attacker can then replay the exact same body/HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value naming a different, victim merchant. `HmacValidator.validate` still succeeds because it never inspects the `shop` header — the equality that should hold, `hmac_signed_shop == handler_shop`, is broken because `shop` is never part of the signed material.

### Impact Explanation
This crosses a tenant boundary: `Registry.process` attributes the (attacker-controlled) event to whichever shop domain the attacker names, not the shop that actually generated it. Any app logic keyed off `WebhookMetadata#shop` (e.g., looking up per-shop session/data, triggering per-shop side effects, or — most severely — invoking the mandatory GDPR handlers for `shop/redact`, `customers/redact`, `customers/data_request`) can be triggered against an arbitrary victim shop identifier supplied by an unrelated, unprivileged installer. This is a cross-tenant identity-confusion vulnerability stemming from the gem's own webhook verification contract.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on a shop they control (trivial — merchant sign-up is free/self-service on Shopify), capture one legitimate webhook delivery from their own store, and replay it with a forged `shop-domain` header to the app's public webhook endpoint. No access to the victim's credentials, access tokens, or `client_secret` is needed. The only shared secret is the app's `client_secret`, which is identical across all installations by design, so the attacker's own valid signature is directly reusable.

### Recommendation
Bind the `shop` field into the material that is HMAC-verified (or otherwise cryptographically tie the header value to the signed body/claims), rather than trusting the `x-shopify-shop-domain` header on its own. At minimum, `Webhooks::Request#to_signable_string` should not be the sole basis for trust when `shop`, `topic`, or `webhook_id` — none of which are covered by the signature — are consumed downstream as authoritative identifiers. Where the parsed body already contains authenticated shop data (e.g., GDPR payloads include the shop id/domain), that field should be cross-checked against the header before use.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com` (self-service, no privilege required).
2. Receive a real webhook delivery, e.g. `orders/create`, and record the raw body `B` and its `X-Shopify-Hmac-Sha256` header `H` (valid because `H = HMAC-SHA256(client_secret, B)`, and `client_secret` is shared across all shops that installed this app).
3. Send a POST to the app's webhook endpoint with body `B` unchanged, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the signature from `B` only and it matches `H`, so validation passes: [5](#0-4) .
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` and dispatches it to the app's handler, which now believes this event/body legitimately originated from `victim.myshopify.com` [6](#0-5) .

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
