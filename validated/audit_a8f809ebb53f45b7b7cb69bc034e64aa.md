### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw body only, while the `shop` (tenant identity) delivered to the app's handler is read from an unsigned HTTP header. Any party capable of producing one valid `(raw_body, hmac)` pair for the app's shared `api_secret_key` (e.g. an attacker who owns their own shop and receives genuine signed webhooks from Shopify for it) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header. `ShopifyAPI::Webhooks::Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` object whose `shop` field is attacker-chosen but whose `body`/`hmac` are legitimately signed — breaking the binding `HMAC(raw_body) over shop` that the app relies on for tenant attribution.

### Finding Description
`to_signable_string` for the webhook request returns only `@raw_body`: [1](#0-0) 

`shop` is derived straight from a header that is not part of the signed material: [2](#0-1) 

`HmacValidator.validate` verifies exactly the bytes returned by `to_signable_string` against the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` only checks this body HMAC, then trusts `request.shop` (the unsigned header) as the tenant identity forwarded to the app's handler: [4](#0-3) 

Because the `api_secret_key` is shared by the app across all installed shops (it is not per-shop), any tenant that has installed the app can obtain a genuinely-signed `(body, hmac)` pair from Shopify for their own store's webhook traffic, then resend that exact pair to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a different shop's domain. The signature still validates (it only covers the body), so `Registry.process` calls the handler with `shop` set to the victim shop while `body` is the attacker's own webhook payload — an identity/tenant binding break: `HMAC(raw_body)` is verified but `shop`, the field the handler acts on for tenant attribution, is not covered by that signature.

### Impact Explanation
This allows cross-tenant data injection: a merchant/attacker who has installed the app can cause the app to process fabricated events under another merchant's shop identity. Depending on how the host application's `WebhookHandler` uses `data.shop` (e.g., to look up per-shop settings, write records, or trigger per-shop side effects), this can lead to cross-tenant state corruption or unauthorized actions attributed to a victim shop — matching the "cross-tenant access" High/Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to have their own working installation of the app (to receive genuinely signed webhooks) and to be able to POST directly to the app's webhook endpoint with forged headers — both are realistic for any app that installs on multiple untrusted merchant shops, since nothing in this gem binds the `shop` header to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind the header-derived tenant identity to the verified payload, instead of trusting an unsigned header for tenant attribution in `ShopifyAPI::Webhooks::Request#shop` and `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook: `raw_body = B`, `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs the same `raw_body = B` and the same valid HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches, since `to_signable_string` only reflects `B`. [5](#0-4) 
4. `Registry.process` invokes the app handler with `WebhookMetadata(topic:, shop: "victim-shop.myshopify.com", body: B, ...)`, even though `B` originated from the attacker's own shop — demonstrating the tenant-identity binding break.

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
