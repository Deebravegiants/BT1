### Title
Shop Domain Header Not Covered by Webhook HMAC Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its webhook authenticity signature over the raw HTTP body only, while the `shop` (tenant) identity used to route webhook data to the handler is taken from an HTTP header that is never included in the signed content. This breaks the intended binding `hmac_valid(raw_body) == authentic_sender(shop)`, allowing an attacker who legitimately receives webhooks for their own store to relabel a captured, validly-signed webhook payload as belonging to a victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` is read directly, unauthenticated, from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Webhooks::Registry.process` validates only the HMAC over the body, then forwards `request.shop` straight to the handler as the tenant identity: [3](#0-2) 

The HMAC (`Utils::HmacValidator.validate`) verifies `computed_signature = HMAC(secret, verifiable_query.to_signable_string)` matches the received `hmac` value — but since `to_signable_string` is exactly `raw_body`, this check is completely independent of the `shop` header: [4](#0-3) 

Because the app's `client_secret`/`api_secret_key` is never known by an unprivileged shop, an attacker cannot forge an HMAC for arbitrary content. However, an attacker who has installed the app on their **own** store legitimately receives real webhook deliveries — each is a genuine `(raw_body, hmac)` pair signed by Shopify. Since the `shop` header is not part of the signed content, the attacker can replay that same valid `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` will happily hand the handler a `WebhookMetadata` claiming `shop: <victim-shop>` together with body content actually produced for the attacker's own store.

The equality that should hold but doesn't:
`shop_that_produced_the_signed_body == request.shop_used_by_handler`

This is exactly the identity-binding gap described by the report's bug class: a field (`shop`) is acted upon by application logic but is not covered by the cryptographic authenticity check (HMAC).

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` (i.e., `request.shop`) to decide which tenant's data to create/update/delete — which is the gem's documented and intended usage pattern — can be tricked into applying an attacker-controlled webhook payload under a victim shop's identity. This is a cross-tenant access vulnerability: a single malicious merchant who has installed the app can inject or manipulate data attributed to another, unrelated shop, without needing the app's `client_secret` or any credential belonging to the victim.

### Likelihood Explanation
The prerequisite is trivial and matches a normal unprivileged usage pattern: the attacker only needs to install the app on their own shop (as any merchant can) to receive real, validly-HMAC-signed webhook deliveries. Capturing and replaying such a request with an altered `shop`-domain header requires no special access, no leaked secrets, and no interaction with the victim.

### Recommendation
Include the shop domain (and any other fields used for authorization/routing decisions, such as topic and webhook id) in the signed content that `HmacValidator` verifies, or otherwise cryptographically bind the header-derived `shop` value to the signed payload before trusting it as tenant identity. At minimum, document that `request.shop` is unauthenticated and must be corroborated against a known, previously-registered shop/session record before being used to select which tenant's data to mutate.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, e.g. `orders/create`, giving them a genuine pair: `raw_body`, `x-shopify-hmac-sha256: <valid hmac over raw_body>`, and header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — succeeds because it's the identical, genuinely-signed body from step 1.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though the payload was never produced for that shop, achieving cross-tenant webhook spoofing.

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
