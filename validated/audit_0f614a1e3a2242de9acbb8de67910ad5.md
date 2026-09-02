### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` binds nothing but the body bytes. The `shop-domain` header — which `Registry.process` reads via `request.shop` and hands to the app's handler as the authoritative tenant identifier in `WebhookMetadata` — is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

Meanwhile `request.shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely independent of the signed body: [4](#0-3) 

After HMAC validation passes, `Registry.process` forwards `request.shop` directly into `WebhookMetadata`, which apps use as the tenant key to route/store the payload: [5](#0-4) [6](#0-5) 

This is the same class of bug as the reported analog: the contract checked one signal (`allowMessagesTo`/message authenticity) but skipped the companion identity check (`allowMessagesFrom`/message origin) before acting on it. Here, the gem checks "was this body signed by our secret" but never checks "was this shop header signed too," yet it treats the header as trusted routing data. The broken identity binding is:

`HMAC-verified(body) == HMAC-verified(shop)` — false. Only the body side of that equality is authenticated; the `shop` field that the handler treats as authenticated tenant identity is not.

### Impact Explanation
Because the HMAC never binds the body to a specific shop, a party with a *valid* body+HMAC pair for one tenant (e.g., a merchant/developer who owns a shop the app is installed on, and can capture webhooks sent to their own endpoint using their own store's legitimate traffic) can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary value in the `shop-domain` header. `HmacValidator.validate` will still pass (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop of the attacker's choosing. Any multi-tenant app that uses `data.shop` (per the documented `WebhookHandler` contract) to decide which tenant's records to create/update/delete is exposed to cross-tenant data injection/corruption — satisfying the "cross-tenant access" impact bucket.

### Likelihood Explanation
Likelihood is low-to-moderate: the attacker needs at least one legitimately signed `(body, hmac)` pair, which is obtainable by anyone who can get a webhook fired for their own trial/dev store on an app that shares the same `api_secret_key` across all tenants (the normal single-secret-per-app Shopify model). No access token, session, or `client_secret` value is needed — only observation of one's own webhook traffic, which is available to any unprivileged user of the app. The blast radius depends on how much of the payload/topic is attacker-controllable and how the host app uses `shop`, but the primitive itself is present in the gem regardless of the host app's care.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in the signable material the HMAC protects, or otherwise cryptographically bind the header to the body before trusting `request.shop` for tenant routing. At minimum, update `Webhooks::Request#to_signable_string` and the validator to fail closed if the header-derived shop cannot be corroborated, and document clearly in `WebhookHandler` that `data.shop` alone is not proof of origin unless this binding is added.

### Proof of Concept
1. App installs on attacker's own store `attacker.myshopify.com`, subscribed to some topic (e.g. `orders/create`).
2. Attacker triggers a webhook for their own store; Shopify sends `POST /webhooks` with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` from their own network traffic (legitimate, no secret leak needed).
4. Attacker replays `POST /webhooks` with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` (per `lib/shopify_api/webhooks/request.rb` line 36-38 and `lib/shopify_api/utils/hmac_validator.rb` line 26-31) — matches `H`, validation passes.
6. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb` line 198-199), causing the app to act on attacker-controlled data attributed to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
