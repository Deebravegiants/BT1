### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop-domain` header — the field the registry uses to attribute the webhook to a tenant — is excluded from the HMAC computation. This breaks the binding: `HMAC(secret, raw_body) == received_hmac` says nothing about which shop the payload belongs to, yet `Registry.process` trusts the unauthenticated `shop-domain` header when dispatching to the handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
only the raw body is signable. The shop identity is read from a separate, unsigned header: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC purely against `to_signable_string`: [3](#0-2) 

`Registry.process` then dispatches to the handler using `request.shop` taken straight from the unauthenticated header, after only checking the (body-only) HMAC: [4](#0-3) 

This is the same class of defect described in the report: a field that is *acted on* (here, the tenant/shop attribution used to route webhook data into per-shop handling logic) is not part of the value that is cryptographically bound (the HMAC). The equality the code should enforce is `hmac == HMAC(secret, raw_body || shop)`, but it actually only enforces `hmac == HMAC(secret, raw_body)`, leaving `shop` free for an attacker to set to any value while keeping the signature valid.

### Impact Explanation
An attacker who legitimately installs the app on their own store (a normal, unprivileged action) will receive genuine Shopify webhooks — valid `raw_body` + valid `hmac` for their own shop's events, addressed to the app's shared webhook endpoint. Because the signature never covers `shop-domain`, the attacker can resend that exact `(raw_body, hmac)` pair to the same webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. The `HmacValidator` still validates successfully (it only checks the body), and `Registry.process` will invoke the app's webhook handler with `WebhookMetadata#shop` set to the victim's domain. Depending on the handler logic, this lets an attacker inject or spoof events (e.g., mandatory compliance webhooks, app/uninstalled, order/customer events) attributed to a shop they do not control — a cross-tenant data-integrity/access break, without any credential belonging to the victim.

### Likelihood Explanation
Likelihood is realistic: obtaining a genuinely-signed `(body, hmac)` pair requires nothing more than installing the app on a shop the attacker controls (trivial, unprivileged), and reusing it against the same endpoint is a straightforward header substitution.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed material, or otherwise cryptographically bind the `shop-domain` header to the HMAC before trusting it in `Registry.process`. Alternatively, cross-check the `shop-domain` header against the shop the webhook subscription was registered for before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`; app registers a webhook (e.g., `orders/create`).
2. Shopify sends a webhook to the app's shared endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, `x-shopify-topic: orders/create`
   - Body: `{...}` (raw JSON, fully controlled/observable by attacker since it's their own order).
3. Attacker resends the identical body and `hmac` to the same endpoint, changing only the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb#L26-L31`) succeeds because it only checks `raw_body` against the HMAC, which is unchanged.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb#L188-L200`) dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", body: ..., topic: "orders/create", ...)` to the handler, causing the app to process attacker-controlled data as if it originated from the victim shop.

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
