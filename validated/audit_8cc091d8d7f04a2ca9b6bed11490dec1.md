## Title
Webhook shop domain is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's handler, but the HMAC signature only covers the raw request body. The `shop` domain — which the gem hands to the handler as the authoritative tenant identifier — is read straight from an unauthenticated HTTP header and is never bound to the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is parsed independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC solely over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses that body-only HMAC check as its sole authentication gate, then immediately trusts the unverified `request.shop` value when building the object passed to the app's handler: [4](#0-3) 

The gem's own documentation instructs integrators to use `data.shop` as the tenant-scoping key for downstream processing (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so this is not a case of the host app ignoring the documented API — it is following it exactly as written.

This breaks the intended identity binding: `hmac_valid(body) == true` should imply `shop == origin_shop_of(body)`, but the gem never establishes that equality — `shop` and `body` are independently attacker-controllable/-observable inputs that are never bound together by the signature.

### Impact Explanation
Any merchant who has installed the app (a normal, unprivileged relationship with the app — no `api_secret_key` or access token needed) receives genuinely Shopify-signed webhook deliveries for their own shop. Because the signature does not cover the shop header, that attacker can replay the captured `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Registry.process` will accept it as valid and dispatch it to the handler labeled as belonging to the victim tenant. Depending on how the host app persists/queues webhook data (as shown in the gem's own documented example), this enables cross-tenant data injection/confusion — data ostensibly from one merchant recorded against another merchant's tenant scope.

### Likelihood Explanation
Any app developer who installed the target app on their own store (a routine, unprivileged action) can obtain a validly-signed webhook body/HMAC pair for arbitrary registered topics at will, then replay it with a forged `shop-domain` header. No secrets, tokens, or privileged access are required.

### Recommendation
Bind the shop identity to the signed payload before trusting it:
- After body HMAC validation succeeds, require the caller to additionally verify `request.shop` against the set of shops that have valid, stored sessions/access tokens for this app (i.e., resolve tenant only from a locally-trusted session store, never from the unauthenticated header alone), or
- Document explicitly and loudly, right next to `Registry.process`, that `shop` is unauthenticated and must be independently checked by the caller against known installed shops before use as a tenant key, rather than implying full request authenticity in `Registry.process`'s behavior/docs.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures this raw request, then resends it to the same endpoint but with the header rewritten to `X-Shopify-Shop-Domain: victim.myshopify.com`, leaving `B` and the HMAC header untouched.
4. `HmacValidator.validate` recomputes `HMAC(secret, B)` — identical to the original — and returns `true`. [4](#0-3) 
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: B, ...)` and, following the gem's documented pattern, persists/queues body `B` under the victim's tenant scope — despite `B` actually originating from the attacker's own shop.

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
