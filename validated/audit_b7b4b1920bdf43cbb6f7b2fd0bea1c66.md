### Title
Webhook Shop Domain Header Not Covered by HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook only via `Utils::HmacValidator.validate(request)`, which validates the HMAC over the raw request body alone. The `shop` value that is subsequently handed to the application's webhook handler is read directly from the unauthenticated `x-shopify-shop-domain` HTTP header, which is never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`, i.e. the body: [2](#0-1) 

Meanwhile `Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the body or the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC, then forwards the header-derived, unauthenticated `shop` value straight to the app's handler as tenant identity: [4](#0-3) 

The equality the design implicitly relies on is:
`shop` authenticated by HMAC == `shop` used as the tenant key (`WebhookMetadata.shop`) passed to the handler.

Because the HMAC covers only the body, and the app's `api_secret_key` is shared across every shop that has installed the app (it is the app's client secret, not a per-shop secret), any merchant who has legitimately installed the app can:
1. Receive genuine webhooks for their own store, each with a valid `(body, hmac)` pair signed with the app's shared secret.
2. Replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it never inspected the header), so `Registry.process` treats the forged request as an authentic webhook "from" the victim shop and invokes the handler with `shop: <victim domain>`.

This breaks the equality "shop authenticated == shop used as tenant identifier" and lets an unprivileged attacker (any shop that installed the app) inject attacker-controlled webhook payloads into another tenant's context.

### Impact Explanation
This satisfies the Critical bar of "cross-tenant access": a webhook body that was legitimately signed for Shop A can be delivered to the host application labeled as originating from victim Shop B. Depending on how the host app trusts `data.shop` (e.g. to select the DB record/session to update, or to process `app/uninstalled`/`shop/redact` type events), this can be used to corrupt, disclose, or manipulate another tenant's data using only a legitimate but unprivileged install of the same app — no access token, secret, or victim credential is required.

### Likelihood Explanation
Exploitation only requires the attacker to install the target Shopify app themselves (which any merchant can do), capture one legitimate webhook delivery (readily available since apps must expose an endpoint receiving these), and replay it with a modified header. This requires no elevated access and no cryptographic secret beyond what any installer already legitimately possesses via their own webhook deliveries.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed payload verification, or otherwise cryptographically bind the `shop` header to the signature — e.g., by validating that the shop domain of the caller matches a shop domain independently known to be associated with `webhook_id`/subscription, or by requiring the host application to cross-check `data.shop` against session storage keyed by a value that is itself HMAC/TLS-verified. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real event (e.g. `orders/create`), receiving a webhook POST with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays the same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and finds it equal to `H` (the shop header was never part of the signed data), so validation passes: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's body B>, ...)`, causing the host app to process attacker-controlled webhook content under the victim's tenant identity.

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
