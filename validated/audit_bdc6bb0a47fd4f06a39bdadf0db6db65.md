### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which tenant the event belongs to when it dispatches to the handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
`Utils::HmacValidator.validate` computes/compares the HMAC solely against `to_signable_string`, i.e. the body bytes: [2](#0-1) 
`Registry.process` checks only this body HMAC, then immediately trusts `request.shop` (an unauthenticated header, `shopify-shop-domain`/`x-shopify-shop-domain`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `hmac_verified_bytes == bytes_that_determine_tenant`. Here it does not — the HMAC only proves body integrity/authenticity relative to `api_secret_key`, it says nothing about which shop the header claims to be. A merchant who has legitimately installed the app (an unprivileged internet user, no special access needed) receives genuinely-signed webhooks for their own store. They can capture one `{raw_body, hmac}` pair from their own legitimate webhook delivery and replay it directly to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. `Registry.process` will still validate the HMAC successfully (it only checks body bytes) and will invoke the handler with `WebhookMetadata.new(shop: <victim shop>, ...)`, causing the host application to process/store attacker-controlled data under the victim shop's identity.

### Impact Explanation
This is a cross-tenant boundary break: an attacker with only their own shop's install can forge webhook events attributed to any other shop, since the shop-domain header used for tenant dispatch is never covered by the cryptographic check. Depending on how the host application's registered handlers use `WebhookMetadata#shop` (e.g., updating that shop's stored data, revoking access, syncing orders/customers), this can lead to cross-tenant data corruption or unauthorized actions performed against a shop the attacker does not control.

### Likelihood Explanation
Requires the attacker to have (or create) a legitimate app installation on at least one shop and trigger any webhook topic to capture a valid `{body, hmac}` pair — an ordinary, unprivileged capability. The webhook HTTP endpoint is a public, unauthenticated ingress documented in `docs/usage/webhooks.md`, and `Registry.process` performs no origin/IP validation or per-tenant secret separation beyond the single shared body HMAC.

### Recommendation
Bind the header fields used for dispatch/authorization to the signature, e.g., include `shop`, `topic`, and `webhook_id` in the signable material (or independently verify that the `shop` header matches a shop the receiving app actually has an active session/install for) before invoking the handler. At minimum, `Registry.process` should cross-check `request.shop` against a known/authorized shop set (e.g., an active session for that shop) rather than trusting the header unconditionally.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook subscription (e.g., `orders/create`), receiving from Shopify a POST with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays this exact request to the app's public webhook endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id` if the handler doesn't need those to match).
3. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)` from the (unmodified) body and it equals `H`, so validation succeeds: [5](#0-4) 
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's own event body>, ...))`, so the host application processes attacker-supplied data as if it originated from the victim shop.

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
