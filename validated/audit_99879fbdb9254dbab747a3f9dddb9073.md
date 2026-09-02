### Title
Webhook `shop` Attribution Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` validates the authenticity of an inbound webhook using only the raw request body as the HMAC-signed material, while the `shop` value used by application code to attribute the webhook to a tenant is read from an HTTP header that is never included in the signature. This breaks the binding `hmac_covers(shop) == shop_used_for_tenant_attribution`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC over the body only (`Utils::HmacValidator.validate(request)` → `verifiable_query.to_signable_string`), and then forwards `request.shop` — the unauthenticated header value — directly to the app's webhook handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signed string is `verifiable_query.to_signable_string` (the body), independent of any header: [4](#0-3) 

Because the HMAC only binds the body bytes and not the shop attribution header, any request that carries a body+signature pair that is valid for *some* shop (e.g., a genuine webhook the attacker legitimately receives for their own installed shop) remains HMAC-valid if the `x-shopify-shop-domain` header is swapped for an arbitrary victim shop domain. `Registry.process` has no additional check tying the header's shop to the shop that actually produced the signed body, so `WebhookMetadata.shop` handed to the app's handler can be forged to any value while `Utils::HmacValidator.validate` still returns `true`. This directly breaks the "shop authenticated vs. shop used as a tenant key" identity binding called out in the analog list.

### Impact Explanation
Multi-tenant apps built on this gem commonly key their datastore, side effects, or subsequent API calls by `WebhookMetadata#shop` (i.e., `request.shop`) once the webhook has passed HMAC validation, treating a positive `HmacValidator.validate` result as proof the payload — including which shop it concerns — is authentic. Since the shop attribution is not part of the signed content, an attacker with a valid signed body (obtainable via their own store's genuine webhook traffic) can cause application logic to associate that body's data with an arbitrary victim shop, producing cross-tenant data confusion/injection in the app's tenant-scoped storage or workflows.

### Likelihood Explanation
Exploitation requires only the ability to receive/capture one legitimately signed webhook body (trivial for anyone who installs the app on their own store, since Shopify signs webhooks with the app's `client_secret` for every subscribed store) and the ability to POST an HTTP request to the app's webhook endpoint with a modified `shop-domain` header — no access to `api_secret_key`, tokens, or any privileged resource is needed.

### Recommendation
Include the shop domain (and other identity-relevant headers, e.g., `webhook-id`, `topic`) in the HMAC-signed material verified by `Utils::HmacValidator`, or otherwise cryptographically bind `request.shop` to the signed body/header set so a captured signature cannot be replayed under a different shop identity. At minimum, document that consumers must not trust `WebhookMetadata#shop` for tenant attribution unless it is independently corroborated (e.g., cross-checked against a registered shop/session store) rather than treating a passing `HmacValidator.validate` as authenticating the shop header.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `client_secret`), header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the same request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`B` only) and successfully matches `H` — see [5](#0-4) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload `B` never originated from or concerned `victim.myshopify.com`, causing the app to process/store attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
