### Title
Webhook Tenant Identity (`shop`) Is Not Bound by the HMAC Signature, Allowing Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely over that body. The `shop` value, read straight from the `X-Shopify-Shop-Domain` header, is never included in the signed material, yet `ShopifyAPI::Webhooks::Registry.process` passes this unauthenticated `shop` value straight into `WebhookMetadata` and into the app's handler as the tenant identity. This breaks the intended binding: `shop-authenticated == shop-used-as-tenant-key`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
returning `@raw_body` only, while `shop` is read from headers independently: [2](#0-1) 

`HmacValidator.validate` computes the signature purely over `to_signable_string` (the body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` only checks this body HMAC before dispatching to the handler with the unauthenticated `shop`: [4](#0-3) 
and `shop` is forwarded verbatim into `WebhookMetadata`, which app code uses as the tenant/store identity: [5](#0-4) 

Because the signature covers only the JSON body, an attacker who has legitimately received one genuine Shopify-signed webhook (e.g., by installing the target app on their own, attacker-controlled shop) possesses a `(body, hmac)` pair that remains cryptographically valid regardless of the `X-Shopify-Shop-Domain` header value. The attacker can replay that same body+hmac to the app's webhook endpoint while substituting a victim shop's domain in the header. `HmacValidator.validate` will still return `true` because the signed content (the body) is unchanged, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion at the library level: the gem asserts (via the passing HMAC check) that the webhook request is authentic and tied to `request.shop`, but no verification actually binds these two facts together. Any host application that uses `WebhookMetadata#shop` to route webhook data (write to the correct tenant's records, look up the correct session, trigger tenant-specific automations, etc.) can be made to process attacker-supplied data under another shop's identity, since the gem's `Registry.process` API provides no facility (and does not require) reverifying that the shop header corresponds to the signed request. This matches the Critical "cross-tenant access" impact category — the vulnerability crosses a tenant boundary using only a validly-signed webhook the attacker legitimately obtained from their own shop installation, no `client_secret`/access token theft required.

### Likelihood Explanation
Likely reachable by any unprivileged internet user: they only need to install the target app on their own store (a normal, unprivileged action for a merchant/attacker) to receive at least one genuine webhook, then replay the exact body+HMAC to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. `Registry.process` and `HmacValidator.validate` provide no defense against this because they never check header/body binding.

### Recommendation
Extend the signable content (or add a secondary check inside `HmacValidator`/`Registry.process`) to bind the `shop-domain`, `topic`, and `webhook-id` headers into the value that's authenticated, or otherwise require the host application/library to cross check that the shop asserted in `WebhookMetadata` matches an actual registered session for that shop before dispatching. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant routing without additional verification (e.g., confirming the shop has an active, previously-established session, or validating the webhook via the `webhook_id`/topic lookup against Shopify's API before acting on it).

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com`, triggers an event (e.g., `orders/create`) and captures the resulting POST: body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and any other headers/topic as needed).
3. `ShopifyAPI::Webhooks::Request.new` accepts the request; `Registry.process` calls `HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`).
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the host application to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
