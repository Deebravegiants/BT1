### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator` validates the HMAC over that string alone. The `shop-domain` header (exposed via `Request#shop`), which `ShopifyAPI::Webhooks::Registry.process` uses to attribute the webhook to a tenant, is never part of the signed material.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, body || shop || topic)`. In this gem it is actually `hmac == HMAC(secret, body)` only: [1](#0-0) [2](#0-1) 

`Registry.process` validates the HMAC, then immediately trusts `request.shop` (parsed straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, with no cross-check against the signed body) to construct the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

Because the `shop` value is read from an unauthenticated header while only the body bytes are verified, an unprivileged internet user who can obtain one valid `(body, hmac)` pair signed with the app's shared secret (e.g., by installing the app on their own shop and capturing a legitimate webhook delivery whose body doesn't itself uniquely encode the shop, such as topics with empty or generic JSON bodies) can resend that exact body+HMAC pair to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header. The signature still validates because the shop identity was never part of the signed bytes, but the handler will process the event as if it came from a different (victim) tenant.

### Impact Explanation
This breaks the shop-authenticated-versus-shop-acted-upon binding (a cross-tenant boundary), matching the report's bug class of "a field acted on but not covered by the HMAC." Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g., to look up and act on a specific merchant's data, or to process mandatory privacy webhooks like `shop/redact`/`customers/redact`), this could let an attacker cause the handler to execute tenant-scoped logic against a shop they do not control — a High-severity cross-tenant integrity issue, though its concrete severity is capped by how much shop-identifying data individual webhook topics' bodies already carry (many topic payloads embed the correct shop's own resource IDs, which would limit — but not eliminate — the practical blast radius for topics with generic/empty bodies).

### Likelihood Explanation
Exploitation requires the attacker to have (or create) a legitimate, unrelated shop installation of the target app to harvest one valid signed webhook body for a topic whose payload does not itself bind the shop, then replay it with a forged shop header — this is unprivileged-internet-user reachable (no `api_secret_key`, access token, or social engineering required) but is topic-dependent, which limits likelihood.

### Recommendation
Include the `shop-domain` (and ideally `topic`) header bytes in the HMAC-signable string in `Request#to_signable_string`/`VerifiableQuery`, or have `Registry.process`/`HmacValidator` independently bind the verified body to the claimed shop before constructing `WebhookMetadata`, so the shop attribution cannot be altered without invalidating the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook topic whose payload body is generic/empty (e.g. `{}`), capturing the raw body and the `x-shopify-hmac-sha256` value Shopify sent.
2. Attacker POSTs to the app's webhook endpoint reusing the exact captured body and HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers; `HmacValidator.validate` recomputes HMAC over `to_signable_string` (body only) and it matches, since the shop header was never part of the signed content.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to act on behalf of a shop the attacker never installed the app on.

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
