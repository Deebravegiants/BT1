### Title
Webhook shop identity is trusted from an unsigned header while only the raw body is HMAC-verified, enabling cross-tenant shop-domain spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` value that is read directly from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body, never this header. Any unprivileged internet user who is able to obtain one validly-signed webhook body/HMAC pair (trivially achievable by triggering a webhook to their own store) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value. `Utils::HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` attribute is the attacker-chosen, unverified value.

### Finding Description
The identity binding that should hold is:

`shop value trusted by the handler (request.shop) == shop value cryptographically bound by the HMAC (to_signable_string)`

In `lib/shopify_api/webhooks/request.rb`:
- `shop` is derived purely from the header: `T.cast(shopify_header("shop-domain"), String)` [1](#0-0) 
- `to_signable_string`, the only material the HMAC actually signs, returns solely `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` and compares it to the received signature: [3](#0-2)  — the `shop` header is never part of the signed material.

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the header is not covered by the signature, the equality above can be broken: the HMAC over a given body will still validate no matter what `shop-domain` header accompanies it, so `request.shop` can be set to any value while `HmacValidator.validate` still returns `true`.

### Impact Explanation
This breaks the tenant-identity boundary this gem is responsible for maintaining before handing verified webhook data to the host application. An attacker who owns any Shopify store (an unprivileged, non-credentialed party with respect to the *victim* merchant) can:
1. Trigger a legitimate webhook to their own shop, capturing a valid `raw_body` + `x-shopify-hmac-sha256` pair signed with the app's shared secret (this is normal, unprivileged app usage — no `api_secret_key` or access token needs to be known or stolen).
2. Replay that exact body and HMAC to the victim app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to the victim shop's domain.
3. `Utils::HmacValidator.validate` still passes (body unchanged), and `Registry.process` calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` reporting the attacker-forged shop.

Any handler that uses `request.shop`/`WebhookMetadata#shop` to select which merchant's records to update, delete, or key by (a common and gem-encouraged pattern; see `docs/usage/webhooks.md`) can be made to apply attacker-controlled body content under a different tenant's identity — i.e., cross-tenant access/confusion, one of the explicitly in-scope Critical impacts.

### Likelihood Explanation
Likelihood is fairly high for an unprivileged attacker: obtaining a validly signed webhook body/HMAC for one's own shop requires nothing more than installing/using the target app's webhook subscription as any legitimate merchant (no leaked secret, no privileged account, no TLS interception). Only the header needs to be forged, which is trivial for any raw HTTP client.

### Recommendation
Bind the shop identity into the value that is actually verified. Options:
- Have `Request#to_signable_string` incorporate the shop-domain header (matching Shopify's documented practice of trusting `X-Shopify-Shop-Domain` only when it is validated against the topic/body context), or
- Independently verify that `request.shop` matches the shop associated with the session/subscription the webhook was registered for before dispatching to the handler, rather than trusting the header value implicitly.

### Proof of Concept
1. As a legitimate merchant, subscribe your own shop (`attacker.myshopify.com`) to a webhook topic and capture the raw POST body and `x-shopify-hmac-sha256` header sent by Shopify.
2. Replay the identical request to the victim app's webhook endpoint, changing only:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` (via `HmacValidator.validate`) accepts the request because the HMAC still matches the unchanged body: [4](#0-3) 
4. The registered `WebhookHandler#handle` is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the body/topic actually originated from the attacker's own shop.

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
