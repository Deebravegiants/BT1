### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC signature against that body alone. The `shop` (tenant identity) is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed bytes. `Registry.process` trusts this unauthenticated header value and forwards it as the tenant identifier to the app's webhook handler.

### Finding Description
`HmacValidator.validate` computes/verifies the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body — the shop header is excluded entirely: [2](#0-1) 

`Registry.process` only checks the HMAC of the body, then blindly trusts `request.shop` (the header value) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because the app's `client_secret` (used as the HMAC key) is the same for every merchant installation of the app, any party who can obtain one validly-signed `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own store and capturing a legitimate webhook delivery to their own endpoint) can replay that exact `raw_body`/`hmac` pair while substituting an arbitrary value in the `shop-domain` header. The signature check in `HmacValidator.validate` still passes — it never inspected the header — so `Registry.process` will invoke the handler with an attacker-chosen `shop` value bound to a payload the attacker fully controls.

This is precisely the "field acted on but not covered by the HMAC" identity-binding break: the equality the gem should enforce is `hmac_signed(shop, body) == received(shop, body)`, but it actually enforces only `hmac_signed(body) == received(body)`, leaving `shop` unauthenticated.

### Impact Explanation
Applications built on this gem commonly use the `shop` field from `WebhookMetadata` to resolve the merchant's stored session/access token or otherwise scope subsequent Admin API actions (this is the documented purpose of `WebhookMetadata#shop`). Since `shop` is not bound to the signature, an attacker can cause the app to process an attacker-controlled payload under a victim shop's identity — a cross-tenant confusion at the point where the gem hands control back to the host application. This matches the Critical "cross-tenant access" category: the gem is the component responsible for authenticating webhook requests, and it fails to bind the tenant identifier into that authentication check.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the vulnerable app on any shop (even a free/attacker-controlled shop, which is normal and unprivileged for any Shopify Partner) to obtain one legitimately-signed `(body, hmac)` pair, and (2) sending a direct HTTP POST to the app's public webhook endpoint with that same body/hmac and a forged `shop-domain` header. No access token, `client_secret`, or privileged credential is needed — only public knowledge of the app's webhook endpoint and a single legitimately captured payload.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signable string/verification input, or independently verify that the shop header corresponds to a shop that has this webhook/topic actually registered, before trusting it. At minimum, `Registry.process` should not treat the header-derived `shop` as authenticated data for authorization decisions without an additional binding to the HMAC.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a legitimate webhook delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid for the app's `client_secret`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. POST directly to the app's public webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` (called in `Registry.process`) validates successfully because it only checks `B` against `H` — the shop header is irrelevant to the check: [4](#0-3) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and `body` fully controlled by the attacker, despite the request never having been signed for that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
