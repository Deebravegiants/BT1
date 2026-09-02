## Finding

### Title
Webhook `shop`-domain header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by checking the HMAC over the raw request body. The `shop` value that the gem hands to the merchant's handler as the authoritative tenant identifier is taken from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header, which is never included in the signed bytes. This breaks the intended binding `hmac_signed_bytes == authenticated_shop`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`HmacValidator.validate` computes the signature over exactly that signable string and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then immediately forwards the unauthenticated `shop` header value to the app's handler: [3](#0-2) 

and `shop` itself is read straight from the header with no cross-check against the signed payload: [4](#0-3) 

Because `api_secret_key` is the same app-level secret shared across every merchant who installs the app, any attacker can install the target app on their own store, receive a legitimately Shopify-signed webhook (valid body + valid HMAC for that body), and then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g. a victim's shop domain). `HmacValidator.validate` will still pass, because it only ever verifies the body, not the header, and the gem will report the event to the handler as `WebhookMetadata` claiming it originated `shop: <victim-shop>`. Any host application that trusts `data.shop` (a normal and encouraged usage pattern, since the gem asserts the request has been "verified") to select which merchant's session/data to act on will now act on the victim tenant using attacker-controlled data — a cross-tenant identity binding violation entirely internal to this gem's verification design.

### Impact Explanation
This is a cross-tenant confusion vulnerability: the gem asserts a webhook is authenticated for shop X, but shop X is attacker-controlled while only the body is verified. Downstream apps that key session/data lookups off `WebhookMetadata#shop` (the documented and expected field for that purpose) can be tricked into applying attacker-supplied webhook data to another merchant's tenant. This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Medium-to-High: no privileged credentials, access tokens, or the app's `client_secret` are needed. The attacker only needs to be a legitimate (even free/trial) merchant of the target app to obtain one genuinely signed body+HMAC pair, then can replay it against arbitrary spoofed `shop` header values indefinitely (the body's HMAC never expires and is not bound to the header).

### Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) in the signable string, or otherwise cryptographically bind the header-derived shop to the verified payload, e.g. by requiring the shop to be present in the JSON body and validating the header matches it, before handing `WebhookMetadata` to the handler. At minimum, document explicitly that `request.shop`/`WebhookMetadata#shop` is unauthenticated header data so integrators do not rely on it for tenant selection.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers/waits for any webhook (e.g. `orders/create`), capturing the raw body `B` and its valid header `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the app's real `api_secret_key`).
2. Attacker POSTs to the same app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only (`Request#to_signable_string` → `@raw_body`) and it matches `H`, so `Registry.process` proceeds.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...))`, causing the host app to process attacker-controlled event data under the victim tenant's identity.

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
