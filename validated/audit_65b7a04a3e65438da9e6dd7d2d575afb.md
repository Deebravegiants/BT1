### Title
Webhook shop/topic identity is not bound to the HMAC-verified payload, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, while the shop domain, topic and webhook id are read from unauthenticated HTTP headers and passed straight through to the app's handler as if they were verified. `Registry.process` validates the HMAC and then hands `request.shop`/`request.topic` to the consuming application's handler without any cryptographic binding between the signed bytes and the claimed tenant/topic, exactly the "field acted on but not covered by the HMAC" class of bug described in the report (there, `issuance.parent_bond` was acted on without being checked against `bond_account_info`).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no relation to the signed content: [2](#0-1) 

`Registry.process` validates only this body-scoped HMAC, then immediately trusts the unauthenticated `request.shop`/`request.topic` values and forwards them to the app's handler as the tenant/topic identity of the payload: [3](#0-2) 

The binding that is broken is:
`HMAC-verified(raw_body)` ≠ `HMAC-verified(raw_body, shop, topic, webhook_id)`

Because a single app's `client_secret`/HMAC key is shared across every shop that has installed the app, any shop that legitimately receives a webhook (a valid `body` + `x-shopify-hmac-sha256` pair) can capture that pair from its own inbound traffic and replay it against the same app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header. `Utils::HmacValidator.validate` will still succeed because it only recomputes the HMAC over `raw_body`: [4](#0-3) 

The handler then receives a `WebhookMetadata` claiming the replayed body belongs to a different shop, with no check that `shop`/`topic` were part of what was actually signed.

### Impact Explanation
This is a cross-tenant identity-binding bypass: a merchant/tenant of a multi-tenant app can make the app process arbitrary (previously-seen, validly-signed) webhook bodies under the identity of a different tenant of the same app, because the shop/topic used for tenant routing is not covered by the signature the gem verifies. Any app logic keyed off `WebhookMetadata#shop` (e.g., updating that shop's stored data, revoking access, writing orders/customers under the "wrong" shop, or unregistering resources) can be triggered cross-tenant — matching the "Critical: cross-tenant access" impact bucket.

### Likelihood Explanation
Exploitation requires no secrets and no privileged access: any actor who is a legitimate merchant/installer of the target app (an "unprivileged internet user" relative to other tenants) can capture one authentic webhook delivery from their own shop and replay it with a forged `shop-domain` (and/or `topic`) header. Because HTTP headers are trivially attacker-controlled and the gem performs no check that they were part of the signed bytes, likelihood is high for any app that relies on `ShopifyAPI::Webhooks::Registry.process` to authenticate the shop/topic of incoming webhooks.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) as part of the signable content that `Utils::HmacValidator` verifies (or otherwise independently corroborate the `shop-domain` header against a value the app already trusts for that installation, e.g. verifying the webhook id/topic pair was actually registered for that shop) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, both using the same `client_secret`.
2. A malicious operator of `shop-a` captures a legitimately delivered webhook: body `B` and header `x-shopify-hmac-sha256: H` (valid for `HMAC(client_secret, B) == H`), plus `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker POSTs the same body `B` and same `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `Registry.process` → `Utils::HmacValidator.validate` succeeds (HMAC only covers `B`), and the handler is invoked with `WebhookMetadata.new(shop: "shop-b.myshopify.com", topic: ..., body: parsed(B), ...)`, causing the app to process `shop-a`'s data as if it belonged to `shop-b`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
