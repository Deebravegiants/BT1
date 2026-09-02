### Title
Webhook `shop` (tenant identifier) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the unauthenticated `X-Shopify-Shop-Domain` header as the tenant identifier passed to the handler. Because the header is not part of the signed data, the binding `hmac-verified bytes == tenant-identifying bytes` does not hold, allowing a shop that legitimately receives a genuine signed webhook to relabel it as belonging to a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is entirely separate from the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body for webhook requests) and compares it against the received `hmac` header: [3](#0-2) 

`Registry.process` only checks this body HMAC, then immediately forwards `request.shop` — the unauthenticated header — to the app's webhook handler as the tenant/shop identifier: [4](#0-3) 

Since the `api_secret_key` used to sign webhooks is shared by the app across every shop that has installed it (not per-shop), any shop that has installed the app receives genuinely, validly-signed webhook deliveries from Shopify for its own store. Because the signature never binds the `shop-domain` header, that shop's operator can capture one of its own valid `(raw_body, hmac)` pairs (particularly easy for topics with fixed/predictable/empty bodies, e.g., `app/uninstalled`, GDPR/compliance topics, or any webhook whose payload the attacker fully controls, such as `orders/create` after placing an order in their own store) and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header value with a victim shop's domain. The `HmacValidator.validate` check still passes because it never inspected the header, and the handler executes with `shop == "victim-shop.myshopify.com"`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: `shop` claimed by the HMAC-authenticated request should equal the `shop` the body was actually generated for/by. An attacker who is a legitimate (but unprivileged relative to other merchants) installer of the app can trigger the app's webhook handler to run business logic (e.g., data deletion/export handling, order/inventory sync, uninstall cleanup) tagged as belonging to a different, victim tenant. Depending on how the host application uses `WebhookMetadata#shop` (e.g., looking up/mutating per-shop state, access tokens, or compliance flows), this can lead to cross-tenant data corruption or disclosure — satisfying the "cross-tenant access" high-impact criterion.

### Likelihood Explanation
Exploitability requires only that the attacker control (or previously receive) one genuinely-signed webhook body for their own shop and be able to POST arbitrary headers to the app's public webhook endpoint — both are available to any ordinary merchant/unprivileged internet actor who can install the target app, with no access to `api_secret_key`, access tokens, or any privileged account. The main constraint is finding a payload that is meaningful/impactful when replayed under a different shop's identity, which is realistic for topics with attacker-influenced or fixed payloads.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind the `shop-domain` header to the signed body before trusting it (e.g., verify that the shop the caller claims matches a shop-scoped secret/session, not just verifying the body against the app-wide secret). At minimum, document and enforce that `WebhookMetadata#shop` must not be treated as authenticated unless additional binding is performed by the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`, thereby causing Shopify to send legitimately-HMAC-signed webhooks to the app's webhook endpoint (e.g. `orders/create` with a body attacker fully controls by placing a crafted order).
2. Attacker captures the raw body and the corresponding `X-Shopify-Hmac-SHA256` value from that legitimate delivery.
3. Attacker POSTs the identical raw body and HMAC header to the same webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the raw body against the shared `api_secret_key`.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled data under the victim's tenant identity.

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
