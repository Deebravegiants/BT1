### Title
Webhook shop identity is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw body only, while the `shop` (tenant identity) is taken from an unsigned HTTP header. `HmacValidator.validate` verifies the HMAC over the body, then `Registry.process` trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler. Because the shop identifier is never part of what is HMAC-verified, an attacker who possesses any one genuine `(body, hmac)` pair (trivially obtainable by installing the app on their own shop and receiving a real webhook) can replay that exact body+HMAC while substituting the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header for a victim shop. The request still passes validation and the handler receives attacker-controlled, victim-attributed webhook data.

### Finding Description
- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#shop` is read straight from an attacker-controlled header, with no cryptographic binding to the signed content: [2](#0-1) 
- `HmacValidator.validate` verifies the signature purely against `verifiable_query.to_signable_string` (the body), never touching `shop`: [3](#0-2) 
- `Registry.process` gates on this body-only HMAC check and then forwards the unauthenticated `request.shop` value straight into the tenant-scoped `WebhookMetadata` delivered to the host application's handler: [4](#0-3) 

The equality that is supposed to hold is: *the shop that authored/authorized the signed body == the shop attributed to the resulting `WebhookMetadata`*. Because the HMAC only covers `@raw_body` and not the `shop-domain` header, this equality is never enforced by the gem — an attacker can decouple the two by keeping a legitimately-signed body/HMAC pair from *their own* shop and swapping only the header naming a different (victim) shop.

### Impact Explanation
This breaks the tenant boundary the webhook mechanism is meant to enforce: any app built on this gem that trusts `WebhookMetadata#shop` (or the underlying `Request#shop`) to determine which tenant a webhook payload belongs to can be made to process forged, attacker-supplied data under a victim shop's identity, since the gem itself performs no binding between the verified bytes and the claimed shop. This is a cross-tenant data-integrity/spoofing issue reachable by any unprivileged internet user who can install the app on a shop of their own (e.g., a free development store) to harvest a valid `(body, hmac)` pair.

### Likelihood Explanation
High likelihood: the attacker does not need the `api_secret_key`, an access token, or any privileged account — only the ability to trigger one webhook delivery for a topic/body shape they need (achievable via a free/dev shop installation of the target app), after which the header swap and replay require nothing more than a basic HTTP client.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified signable content, or otherwise cryptographically tie the declared shop to the verified request (e.g., verify the shop against a value derived from Shopify-issued, per-shop webhook secrets, or require the app to cross-check `request.shop` against its own list of installed/authorized shops before trusting it). At minimum, document prominently that `Request#shop` is unauthenticated and must not be used as a tenant key without independent verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the genuine raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify over `B` with the app's real secret).
2. Attacker sends a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` and compares against `H` — it succeeds because `B` and `H` are unchanged and genuinely matched.
4. `Registry.process` proceeds to build `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim.myshopify.com"`, and invokes the app's handler as if this were a legitimate webhook for the victim shop. [4](#0-3)

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
