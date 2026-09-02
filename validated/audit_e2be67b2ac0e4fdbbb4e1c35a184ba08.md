### Title
Webhook `shop-domain` Header Not Covered by HMAC Validation Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` and `ShopifyAPI::Utils::HmacValidator.validate` only bind the HMAC signature to the raw request body, but never to the `shop-domain` header that `ShopifyAPI::Webhooks::Registry.process` uses to identify which shop a webhook belongs to. An attacker who possesses one valid (self-installed, legitimately signed) webhook can replay it while substituting an arbitrary `shop-domain` value, and the request still passes HMAC validation, since that header is never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes and compares the HMAC solely against `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` only checks this body-only HMAC, then trusts `request.shop` (derived straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

The identity binding the gem claims to enforce is: **`hmac` valid ⇒ (`body`, `shop`, `topic`) is authentic**. In reality the equality it actually verifies is only **`hmac` valid ⇒ `body` is authentic**; `shop` (and `topic`) are parsed from headers that sit entirely outside the signed payload. Because the raw body and its HMAC are decoupled from the `shop` header, any party capable of obtaining one genuine `(body, hmac)` pair — e.g., a merchant who legitimately installs the app on their own store and thus legitimately receives Shopify webhooks signed with the app's real `api_secret_key` — can resend that same body/HMAC pair to the app's webhook endpoint with a different `shopify-shop-domain` header value naming a *different* shop. `HmacValidator.validate` will still return `true`, since it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the attacker-chosen shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee to consumers of `Registry.process`/`WebhookHandler#handle`: webhook data can be attributed to a shop other than the one that actually produced it. Any host application that uses `data.shop` from `WebhookMetadata` to key session/data lookups (the intended and documented usage pattern) can be made to apply another shop's webhook body under a victim shop's identity — a cross-tenant access/data-confusion primitive. This satisfies the Critical impact bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Likelihood is low-to-moderate: the attacker needs at least one genuinely signed `(body, hmac)` pair, which any merchant who installs the app on their own shop can obtain trivially and then replay against the shared public webhook endpoint with a forged `shop-domain` header — no possession of the `api_secret_key` itself is required, only a single legitimately-received webhook payload.

### Recommendation
Include the shop domain (and topic) inside the signed material that `HmacValidator` verifies, or otherwise cryptographically bind `request.shop` to the validated payload before it is trusted in `Registry.process`. At minimum, `to_signable_string` should incorporate the `shopify-shop-domain` header (mirroring how Shopify's own webhook signing already covers the full raw body) so tampering with the shop header invalidates the HMAC, and/or `Registry.process` should independently confirm that the resolved shop is consistent with an installed/known session before dispatching to `handler.handle`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, and a correctly computed `x-shopify-hmac-sha256` over `B`.
2. Attacker replays the exact same `B` and `hmac` to the app's webhook endpoint but rewrites the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into `request.shop == "victim.myshopify.com"` while `request.to_signable_string == B` is unchanged.
4. `Utils::HmacValidator.validate(request)` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:13-22`) because only `B` is checked.
5. `Registry.process` (per `lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data under the victim shop's identity.

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
