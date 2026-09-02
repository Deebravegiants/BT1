### Title
Webhook Shop-Domain Header Is Not Covered by the HMAC, Allowing Cross-Tenant Shop Spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw webhook body [1](#0-0) , while `shop` is read verbatim from the unsigned `x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates the HMAC over that body only, then trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler [3](#0-2) . The identity binding that should hold is: `shop asserted in header == shop that produced/authorized the signed body`. Because the header is outside the HMAC, that equality is never enforced.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` header using `OpenSSL.secure_compare` [4](#0-3) . For webhooks, `to_signable_string` is just `@raw_body` [1](#0-0) ; none of the headers, including `shop-domain`, factor into the signature. Since a single Shopify app uses one shared `api_secret_key` for HMAC validation across every merchant that installs it [5](#0-4) , any merchant who installs the app receives their own legitimately-signed `(body, hmac)` pair for their own webhooks. That pair remains valid under `HmacValidator.validate` regardless of which `x-shopify-shop-domain` header accompanies it, because the header isn't part of the signed content.

`Registry.process` only checks `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop` to construct `WebhookMetadata` dispatched to the host app's handler [3](#0-2) . There is no check inside the gem that the asserted `shop` is consistent with anything cryptographically tied to the request.

### Impact Explanation
An unprivileged attacker who is merely a legitimate (if low-value) installer of the target app on their own store can capture one of their own genuine webhook deliveries (a valid `raw_body` + `x-shopify-hmac-sha256` pair, both fully within their control/knowledge since it's their own shop's webhook) and replay it to the app's webhook endpoint while substituting `x-shopify-shop-domain` with a victim merchant's domain. `HmacValidator.validate` still passes since only the body is checked, and `Registry.process` forwards `shop: <victim domain>` to the handler. If the host application relies on the gem's webhook `shop` field (as documented/intended usage) to select the tenant session, store record, or authorization context, this results in cross-tenant data confusion/access — data or actions intended for the attacker's own shop get attributed to another merchant's tenant.

### Likelihood Explanation
Any user can become a legitimate installer of a public app (this is the "unprivileged internet user" position), and no elevated privilege, secret leakage, or TLS interception is required — the attacker generates and observes their own valid signed webhook and merely re-sends it with a different header value. The only dependency is the host app trusting `WebhookMetadata#shop` for tenant-sensitive decisions, which is the documented and expected usage pattern for `Registry.process`/`WebhookHandler#handle`.

### Recommendation
Bind the shop identity to the signed content instead of trusting an unsigned header:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) in the signable string used for HMAC computation, or
- Cross-check `request.shop` against an independently-verified source (e.g., the topic/webhook registration or a shop-scoped secret) before constructing `WebhookMetadata`, and
- Document/enforce that host applications must not rely solely on the unsigned `shop` header for tenant attribution unless the gem itself binds it into the HMAC-verified payload.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only [1](#0-0) [4](#0-3) , which still matches `H`, so validation succeeds.
4. `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"` [3](#0-2) , even though the payload `B` was never authorized by or associated with `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
